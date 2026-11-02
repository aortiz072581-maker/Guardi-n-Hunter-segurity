package guardian.authorization

default allow := false

allow if {
	input.human_review_required == true

	input.execution_allowed == false
	input.merge_allowed == false
	input.commit_allowed == false
	input.baseline_update_allowed == false
	input.global_execution_allowed == false

	valid_sha256(input.proposal_hash)
	valid_sha256(input.policy_hash)
	valid_baseline(input.baseline)

	input.proposal_hash == input.approved_proposal_hash
	input.policy_hash == input.approved_policy_hash
	input.baseline == input.approved_baseline
}

valid_sha256(value) if {
	regex.match("^[0-9a-f]{64}$", value)
}

valid_baseline(value) if {
	regex.match("^[0-9a-f]{40}$", value)
}
