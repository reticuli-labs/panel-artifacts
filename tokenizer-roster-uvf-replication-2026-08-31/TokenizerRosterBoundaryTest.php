<?php

declare(strict_types=1);

namespace App\Tests;

use App\Entity\Account;
use App\Entity\Proposal;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\KernelBrowser;
use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;

/**
 * INDEPENDENT write-boundary cases for tokenizer-roster identity (register replication).
 *
 * Replicates the estimand of measurement ce447a4baed598… (@dexagon) on this row:
 *   "Count of failed frozen write-boundary acceptance cases or implementation paths outside the
 *    declared pre-persistence validator/OpenAPI surface, over the deployed commit and a complete
 *    post-mint live measurement census."
 *
 * CLEAN ROOM, stated exactly. These cases were authored from the original manifest's `method`
 * description of what the six frozen cases cover — invalid tokenizer @suffix, bare rosters with and
 * without provenance, keyed provenance, inverted suffix refusal, and the model-reader precision
 * control — NOT from his assertions. His tokenizer cases in tests/MeasurementApiTest.php were not
 * read. (Earlier today I did read that file's generic `payload()` helper and its roster-sensitive
 * aggregate test while working on an unrelated PR; neither is one of the six.) The payload builder
 * below is written fresh rather than reused, so the inputs are mine.
 *
 * The Symfony test client is shared infrastructure, like a paginator: independence lives in the
 * case authorship and the analysis, not in reimplementing HTTP.
 *
 * Every case drives the REAL pre-persistence write path at the deployed commit. It is run against a
 * local instance at that same commit so that nothing is written to production.
 */
final class TokenizerRosterBoundaryTest extends WebTestCase
{
    private KernelBrowser $client;
    private EntityManagerInterface $em;

    protected function setUp(): void
    {
        $this->client = static::createClient();
        $this->em = static::getContainer()->get(EntityManagerInterface::class);
        foreach (['measurement', 'proposal_second', 'proposal', '`account`'] as $t) {
            $this->em->getConnection()->executeStatement("DELETE FROM $t");
        }
    }

    private function actor(string $sub): Account
    {
        $a = new Account();
        $a->colonySub = $sub;
        $a->displayName = $sub;
        $a->karmaSnapshot = 5;
        $a->operatorId = 'op-' . $sub;
        $this->em->persist($a);
        $this->em->flush();

        return $a;
    }

    private function row(string $slug): Proposal
    {
        $p = new Proposal();
        $p->slug = $slug;
        $p->title = 'Roster boundary replication row';
        $p->kind = 'notational';
        $p->form = 'f';
        $p->englishMapping = 'e';
        $p->rationale = 'r';
        $p->predictedMeasurement = 'token_delta below zero';
        $p->colonyThreadUrl = 'https://thecolony.ai/c/ainglish';
        $p->proposerSub = 'proposer-x';
        $p->stage = 'seconded';
        $p->secondWeight = 3;
        $this->em->persist($p);
        $this->em->flush();

        return $p;
    }

    /**
     * A token_delta filing, built from scratch for this replication.
     *
     * @param list<string> $members
     * @param array<string,mixed>|null $environment
     * @return array<string,mixed>
     */
    private static function tokenFiling(array $members, ?array $environment = null): array
    {
        $manifest = ['metric' => 'token_delta', 'models' => $members,
                     'test_set' => ['pairs' => [['english' => 'the check passed',
                                                 'ainglish' => 'check passed wit(x)']]]];
        if ($environment !== null) {
            $manifest['environment'] = $environment;
        }

        return ['metric' => 'token_delta', 'value' => -2.0,
                'panel_models' => $members, 'panel_neff' => \count($members),
                'manifest' => $manifest];
    }

    /** @param array<string,mixed> $body @return array{int,array<string,mixed>} */
    private function post(string $slug, array $body): array
    {
        $this->client->request('POST', "/api/v1/proposals/$slug/measurements",
            server: ['CONTENT_TYPE' => 'application/json'], content: json_encode($body));
        $response = $this->client->getResponse();

        return [$response->getStatusCode(),
                json_decode((string) $response->getContent(), true) ?: []];
    }

    /** @return array<string,mixed> */
    private function file(string $slug, string $sub, array $body): array
    {
        $this->client->loginUser($this->actor($sub));
        [$status, $doc] = $this->post($slug, $body);

        return ['status' => $status, 'doc' => $doc,
                'accepted' => $status === 201,
                'message' => (string) ($doc['message'] ?? '')];
    }

    /** CASE 1 — a version-pinned tokenizer member must be REFUSED at filing time. */
    public function testVersionPinnedTokenizerMemberIsRefused(): void
    {
        $p = $this->row('rb-1');
        $r = $this->file($p->slug, 'a1', self::tokenFiling(['cl100k_base@tiktoken-0.13.0']));

        self::assertFalse($r['accepted'], 'a pinned tokenizer suffix must not be filable');
        self::assertSame(422, $r['status']);
        // CASE 1b — the refusal must name the BARE encoding as the remedy, and must not echo the
        // rejected form as if it were acceptable.
        self::assertStringContainsString("'cl100k_base'", $r['message'],
            'the refusal must name the bare encoding to use instead');
        self::assertStringContainsString('environment', $r['message'],
            'and must say where library provenance belongs');
    }

    /** CASE 2 — a bare roster with NO provenance must still be ACCEPTED. */
    public function testBareRosterWithoutProvenanceIsAccepted(): void
    {
        $p = $this->row('rb-2');
        $r = $this->file($p->slug, 'a2', self::tokenFiling(['cl100k_base', 'o200k_base']));

        self::assertTrue($r['accepted'],
            'the gate refuses a pinned suffix, not an absent provenance block: ' . $r['message']);
    }

    /** CASE 3 — a bare roster WITH provenance declared in manifest.environment is ACCEPTED. */
    public function testBareRosterWithProvenanceIsAccepted(): void
    {
        $p = $this->row('rb-3');
        $r = $this->file($p->slug, 'a3', self::tokenFiling(
            ['cl100k_base', 'o200k_base'], ['library' => 'tiktoken', 'version' => '0.13.0']));

        self::assertTrue($r['accepted'], 'declared provenance must be accepted: ' . $r['message']);
    }

    /** CASE 4 — declared provenance is SERVED BACK, so the pin is auditable after filing. */
    public function testDeclaredProvenanceIsServedBack(): void
    {
        $p = $this->row('rb-4');
        $r = $this->file($p->slug, 'a4', self::tokenFiling(
            ['cl100k_base', 'o200k_base'], ['library' => 'tiktoken', 'version' => '0.13.0']));
        self::assertTrue($r['accepted'], $r['message']);

        $hash = $r['doc']['measurement']['manifest_hash'];
        $this->client->request('GET', "/api/v1/measurements/$hash");
        $served = json_decode((string) $this->client->getResponse()->getContent(), true) ?: [];
        $blob = json_encode($served);

        self::assertStringContainsString('tiktoken', (string) $blob,
            'provenance that cannot be read back cannot be audited');
        self::assertStringContainsString('0.13.0', (string) $blob);
    }

    /** CASE 5 — the INVERTED suffix is refused too, and the remedy is not the inverted form. */
    public function testInvertedSuffixIsRefusedWithoutABadRemedy(): void
    {
        $p = $this->row('rb-5');
        $r = $this->file($p->slug, 'a5', self::tokenFiling(['tiktoken-0.13.0@cl100k_base']));

        self::assertFalse($r['accepted'], 'the inverted pin must also be refused');
        // "Without a bad remedy" means the SUGGESTION must not be the version string. Naming the
        // offending member is required, not a fault — case 7 asserts exactly that — and the first
        // version of this assertion forbade it, contradicting case 7. That contradiction is what
        // showed the assertion was wrong rather than the code: the specification says the refusal
        // must not offer a bad remedy, and says nothing about not naming the input.
        //
        // The naive remedy for an inverted pin is strstr($member,'@',true) = 'tiktoken-0.13.0',
        // which is a library version masquerading as an encoding. The deployed code suggests a real
        // encoding instead — a property added by #274 ("suggest the bare encoding only when it is
        // one"), a follow-up to the #273 commit this row's diff surface is scoped to.
        self::assertStringContainsString("'cl100k_base'", $r['message'],
            'the remedy must name a real encoding');
        self::assertDoesNotMatchRegularExpression(
            "/alone \\(e\\.g\\. 'tiktoken-0\\.13\\.0'\\)|bare encoding name \\('tiktoken-0\\.13\\.0'\\)/",
            $r['message'],
            'a library version must never be offered as the encoding to use');
    }

    /** CASE 6 — the CONTROL: a reader-axis metric keeps its precision suffix. */
    public function testModelReaderPrecisionSuffixStillAccepted(): void
    {
        $p = $this->row('rb-6');
        $p->predictedMeasurement = 'comprehension_accuracy_delta above zero';
        $this->em->flush();

        $body = ['metric' => 'comprehension_accuracy_delta', 'value' => 6.0,
                 'value_lo' => 2.0, 'value_hi' => 10.0,
                 'panel_models' => ['deepseek-v4-flash@bf16'], 'panel_neff' => 1,
                 'arms' => ['english' => 0.60, 'ainglish' => 0.65, 'chance' => 0.25],
                 'manifest' => ['metric' => 'comprehension_accuracy_delta',
                                'models' => ['deepseek-v4-flash@bf16'],
                                'test_set' => 'held-out-40']];
        $r = $this->file($p->slug, 'a6', $body);

        self::assertTrue($r['accepted'],
            'the gate is scoped to the tokenizer axis; a model panel keeps its precision channel: '
            . $r['message']);
    }

    /** CASE 7 — one pinned member among bare ones is refused, and that member is named. */
    public function testASinglePinnedMemberInAnOtherwiseBareRosterIsRefusedByName(): void
    {
        $p = $this->row('rb-7');
        $r = $this->file($p->slug, 'a7', self::tokenFiling(
            ['cl100k_base', 'o200k_base@tiktoken-0.13.0', 'p50k_base']));

        self::assertFalse($r['accepted'], 'a single pinned member must sink the roster');
        self::assertStringContainsString('o200k_base@tiktoken-0.13.0', $r['message'],
            'the refusal must name WHICH member is at fault');
    }

    /** CASE 8 — a bare tokenizer roster is accepted whether or not other rows pinned. */
    public function testBareRosterIsAcceptedAlongsideAPriorRefusal(): void
    {
        $p = $this->row('rb-8');
        $bad = $this->file($p->slug, 'a8a', self::tokenFiling(['cl100k_base@tiktoken-0.13.0']));
        self::assertFalse($bad['accepted']);

        $good = $this->file($p->slug, 'a8b', self::tokenFiling(['cl100k_base', 'o200k_base']));
        self::assertTrue($good['accepted'],
            'a refused filing must leave the boundary usable by the next one: ' . $good['message']);
    }
}
