<?php

declare(strict_types=1);

namespace App\Tests;

use App\Entity\Proposal;
use App\Repository\GateEventRepository;
use App\Repository\ProposalRepository;
use App\Service\AdoptionService;
use App\Service\RegisterLedger;
use Doctrine\ORM\EntityManagerInterface;
use Doctrine\Persistence\ManagerRegistry;
use Symfony\Bundle\FrameworkBundle\Test\KernelTestCase;

/**
 * Measurement harness, not a regression test of the register. It is copied into the audited checkout
 * for one run and removed afterwards.
 *
 * It loads ONE frozen population into the test database, moved forward in time by a whole number of
 * days, and asks three versions of the adoption rule what they would serve for every row:
 *
 *   OLD  the class as it stood before the change       (git blob, class renamed, nothing else)
 *   MID  the class as first deployed                    (git blob, class renamed, nothing else)
 *   NEW  the class in this checkout, which the runner has shown byte-identical to production
 *
 * It counts nothing. It writes the raw table; the runner applies the counting rule.
 */
final class UnscannedIsNotZeroUvfHarnessTest extends KernelTestCase
{
    private const DIR = __DIR__ . '/_uvf_unscanned';
    private const TABLES = [
        'content_report_review_event', 'content_report', 'proposal_slug', 'proposal_stage_transition', 'proposal_work_notice',
        'adoption_snapshot', 'adoption_observation', 'attestation', 'ratification_vote', 'attempt', 'measurement',
        'proposal_second', 'gate_event', 'register_event', 'proposal',
    ];

    public function testProjectEveryArm(): void
    {
        $config = self::json(self::DIR . '/config.json');
        $population = self::json(self::DIR . '/' . $config['population_file']);
        self::assertSame(hash_file('sha256', self::DIR . '/' . $config['population_file']), $config['population_sha256'], 'the population file is not the frozen one');
        foreach (['Old', 'Mid'] as $arm) {
            require_once self::DIR . '/AdoptionObservationRepositoryUvf' . $arm . '.php';
            require_once self::DIR . '/AdoptionServiceUvf' . $arm . '.php';
        }

        self::bootKernel();
        $c = static::getContainer();
        /** @var EntityManagerInterface $em */
        $em = $c->get(EntityManagerInterface::class);
        /** @var ManagerRegistry $registry */
        $registry = $c->get('doctrine');
        $proposals = $c->get(ProposalRepository::class);
        $ledger = $c->get(RegisterLedger::class);
        $gateEvents = $c->get(GateEventRepository::class);
        $services = [
            'OLD' => new \App\Service\AdoptionServiceUvfOld($em, new \App\Repository\AdoptionObservationRepositoryUvfOld($registry), $proposals, $ledger, $gateEvents),
            'MID' => new \App\Service\AdoptionServiceUvfMid($em, new \App\Repository\AdoptionObservationRepositoryUvfMid($registry), $proposals, $ledger, $gateEvents),
            'NEW' => $c->get(AdoptionService::class),
        ];
        self::assertSame('UTC', date_default_timezone_get());

        $t0 = new \DateTimeImmutable($population['t0']);
        $startedAt = new \DateTimeImmutable('now', new \DateTimeZone('UTC'));
        $wholeDays = intdiv($startedAt->getTimestamp() - $t0->getTimestamp(), 86_400);
        self::assertGreaterThan(0, $wholeDays);

        $out = [
            'kind' => 'reticuli.unscanned-uvf.raw.v1',
            'population_sha256' => $config['population_sha256'],
            't0' => $population['t0'],
            'run_started_at' => $startedAt->format(\DATE_ATOM),
            'whole_days_between_t0_and_run' => $wholeDays,
            'evaluation_instant_at_offset_0' => $startedAt->modify('-' . $wholeDays . ' days')->format(\DATE_ATOM),
            'php_version' => \PHP_VERSION,
            'database' => $em->getConnection()->fetchOne('SELECT VERSION()'),
            'cells' => [],
            'sweeps' => [],
        ];

        foreach ($config['cells'] as $cell) {
            $arm = $cell['arm'];
            $offset = (int) $cell['clock_offset_days'];
            self::assertArrayHasKey($arm, $services);
            $shift = $wholeDays - $offset;
            $this->load($em, $population, $config['plants'], $shift, $startedAt);
            $em->clear();

            $rows = [];
            foreach ($proposals->findBy([], ['slug' => 'ASC']) as $p) {
                $reading = $arm === 'OLD'
                    ? ['status' => $services['OLD']->status($p), 'recent_usage' => $services['OLD']->recentUsage($p)]
                    : $services[$arm]->summary($p);
                self::assertArrayHasKey('status', $reading);
                self::assertArrayHasKey('recent_usage', $reading);
                $rows[$p->slug] = ['status' => $reading['status'], 'recent_usage' => $reading['recent_usage']];
            }
            $expected = \count($population['rows']) + \count($config['plants']);
            self::assertCount($expected, $rows, 'every row of the population and every plant must be read');
            $out['cells'][] = ['arm' => $arm, 'clock_offset_days' => $offset, 'shift_days' => $shift, 'rows' => $rows];

            if (($cell['sweep'] ?? false) === true) {
                $result = $services[$arm]->sweepDeprecated();
                $em->clear();
                $after = [];
                foreach ($proposals->findBy([], ['slug' => 'ASC']) as $p) {
                    $after[$p->slug] = ['stage' => $p->stage, 'deprecated_reason' => $p->deprecatedReason];
                }
                $out['sweeps'][] = ['arm' => $arm, 'clock_offset_days' => $offset, 'result' => $result, 'rows' => $after];
            }
        }

        $out['run_finished_at'] = (new \DateTimeImmutable('now', new \DateTimeZone('UTC')))->format(\DATE_ATOM);
        $dest = \dirname(__DIR__) . '/var/uvf_unscanned_raw.json';
        file_put_contents($dest, json_encode($out, \JSON_PRETTY_PRINT | \JSON_UNESCAPED_SLASHES | \JSON_THROW_ON_ERROR) . "\n");
        self::assertFileExists($dest);
        self::assertCount(\count($config['cells']), $out['cells']);
    }

    /**
     * @param array<string,mixed> $population
     * @param list<array<string,mixed>> $plants
     */
    private function load(EntityManagerInterface $em, array $population, array $plants, int $shift, \DateTimeImmutable $runStartedAt): void
    {
        $db = $em->getConnection();
        foreach (self::TABLES as $table) {
            $db->executeStatement("DELETE FROM $table");
        }
        $em->clear();
        $move = static fn (string $iso): \DateTimeImmutable => (new \DateTimeImmutable($iso))->modify(($shift >= 0 ? '+' : '-') . abs($shift) . ' days');

        $ids = [];
        foreach ($population['rows'] as $row) {
            $ids[$row['slug']] = $this->proposal(
                $em, $row['slug'], $row['kind'],
                $row['in_population'] ? 'ratified' : $row['stage_in_snapshot'],
                $row['in_population'] ? $move($row['ratified_at']) : null,
                $move($row['created_at']),
            );
        }
        foreach ($population['observations'] as $o) {
            $this->observation($db, $ids[$o['slug']], $o['source'], $move($o['window_start'] . 'T00:00:00Z'), $move($o['window_end'] . 'T00:00:00Z'), $o['usage_count'], $move($o['created_at']), $o['detector_version'], $o['scan_count']);
        }

        // Plants are placed relative to the evaluation instant of THIS cell, which is the run start
        // moved back by the cell's clock offset in the population's own timeline. In the loaded
        // (moved) timeline that instant is the run start itself minus nothing: every cell is read "now".
        foreach ($plants as $plant) {
            $ratifiedAt = $runStartedAt->modify('-' . $plant['ratified_days_before_evaluation'] . ' days');
            $id = $this->proposal($em, $plant['slug'], 'notational', 'ratified', $ratifiedAt, $ratifiedAt->modify('-5 days'));
            foreach ($plant['scans'] as $scan) {
                $createdAt = $runStartedAt->modify('-' . $scan['created_days_before_evaluation'] . ' days');
                $windowEnd = $runStartedAt->modify('-' . $scan['window_end_days_before_evaluation'] . ' days')->setTime(0, 0);
                $this->observation($db, $id, $scan['source'], $windowEnd->modify('-30 days'), $windowEnd, $scan['usage_count'], $createdAt, null, null);
            }
        }
    }

    private function proposal(EntityManagerInterface $em, string $slug, string $kind, string $stage, ?\DateTimeImmutable $ratifiedAt, \DateTimeImmutable $createdAt): int
    {
        $p = new Proposal();
        $p->slug = $slug;
        $p->title = $slug;
        $p->kind = $kind;
        $p->form = $slug;
        $p->englishMapping = 'Population row.';
        $p->rationale = 'Population row.';
        $p->predictedMeasurement = 'Population row.';
        $p->colonyThreadUrl = 'https://thecolony.ai/c/ainglish';
        $p->proposerSub = 'population';
        $p->stage = $stage;
        $p->createdAt = $createdAt;
        if ($stage === 'ratified') {
            $p->ratifiedVersion = '0.1.0';
            $p->ratifiedAt = $ratifiedAt;
        }
        $em->persist($p);
        $em->flush();
        self::assertNotNull($p->id);
        self::assertTrue($p->isPublished());

        return (int) $p->id;
    }

    private function observation(\Doctrine\DBAL\Connection $db, int $proposalId, string $source, \DateTimeImmutable $start, \DateTimeImmutable $end, int $usage, \DateTimeImmutable $createdAt, ?string $detector, ?int $scanCount): void
    {
        $db->executeStatement(
            'INSERT INTO adoption_observation (proposal_id, source, window_start, window_end, usage_count, note, detector_version, corpus, scan_count, created_at) VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, ?, ?)',
            [$proposalId, $source, $start->format('Y-m-d'), $end->format('Y-m-d'), $usage, $detector, $scanCount, $createdAt->format('Y-m-d H:i:s')],
        );
    }

    /** @return array<string,mixed> */
    private static function json(string $path): array
    {
        return json_decode((string) file_get_contents($path), true, flags: \JSON_THROW_ON_ERROR);
    }
}
