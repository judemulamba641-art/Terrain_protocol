from submission import BugSubmission
from dao_checker import is_approved
from reward_executor import execute_reward
from cooldown import can_claim, register_claim

submission = BugSubmission(
    reporter="0xResearcher",
    description="NFT oracle manipulation via floor spoofing...",
    severity=9,
    reproducible=True
)

proposal_id = 12

if not submission.is_valid():
    raise Exception("Invalid submission")

if not is_approved(proposal_id):
    raise Exception("DAO has not approved")

if not can_claim(submission.reporter):
    raise Exception("Cooldown active")

tx = execute_reward(proposal_id)
register_claim(submission.reporter)

print("✅ Bug bounty rewarded:", tx)
