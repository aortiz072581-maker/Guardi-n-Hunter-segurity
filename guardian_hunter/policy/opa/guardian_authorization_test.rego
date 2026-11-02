package guardian.authorization

valid_input := {
	"human_review_required": true,
	"execution_allowed": false,
	"merge_allowed": false,
	"commit_allowed": false,
	"baseline_update_allowed": false,
	"global_execution_allowed": false,
	"proposal_hash": sprintf("%064s", ["a"]),
	"policy_hash": sprintf("%064s", ["b"]),
	"baseline": sprintf("%040s", ["c"]),
	"approved_proposal_hash": sprintf("%064s", ["a"]),
	"approved_policy_hash": sprintf("%064s", ["b"]),
	"approved_baseline": sprintf("%040s", ["c"]),
}

test_exact_context_allowed if {
	allow with input as valid_input
}

test_execution_escalation_denied if {
	not allow with input as object.union(
		valid_input,
		{"execution_allowed": true},
	)
}

test_merge_escalation_denied if {
	not allow with input as object.union(
		valid_input,
		{"merge_allowed": true},
	)
}

test_commit_escalation_denied if {
	not allow with input as object.union(
		valid_input,
		{"commit_allowed": true},
	)
}

test_baseline_authority_denied if {
	not allow with input as object.union(
		valid_input,
		{"baseline_update_allowed": true},
	)
}

test_global_execution_denied if {
	not allow with input as object.union(
		valid_input,
		{"global_execution_allowed": true},
	)
}

test_human_review_bypass_denied if {
	not allow with input as object.union(
		valid_input,
		{"human_review_required": false},
	)
}

test_proposal_mutation_denied if {
	not allow with input as object.union(
		valid_input,
		{
			"proposal_hash": sprintf("%064s", ["d"]),
		},
	)
}

test_policy_mutation_denied if {
	not allow with input as object.union(
		valid_input,
		{
			"policy_hash": sprintf("%064s", ["e"]),
		},
	)
}

test_baseline_mutation_denied if {
	not allow with input as object.union(
		valid_input,
		{
			"baseline": sprintf("%040s", ["f"]),
		},
	)
}
