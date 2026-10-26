"""Fail closed on publication inputs before building or logging into a registry."""
import argparse
import json
import re
from pathlib import Path


def validate(tag, flavor, expected_source, actual_source):
    if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-rc\.?\d+)?(?:-(?:cpu|cuda128))?', tag, flags=re.ASCII):
        raise ValueError('Tag must be a version or release-candidate version, optionally suffixed with its flavor')
    if flavor not in ('cpu', 'cuda128'):
        raise ValueError('Unsupported PyTorch flavor')
    if re.search(r'-(cpu|cuda128)$', tag) and not tag.endswith('-' + flavor):
        raise ValueError('Tag suffix does not match the selected flavor')
    if not re.fullmatch(r'[0-9a-f]{40}', expected_source, flags=re.ASCII):
        raise ValueError('Expected source must be a complete lowercase Git commit SHA')
    if actual_source != expected_source:
        raise ValueError('Dispatch source differs from the approved source')


def validate_environment(environment, policies):
    if environment.get('name') != 'official-release':
        raise ValueError('The official-release environment is required')
    reviewers = [r for r in environment.get('protection_rules', []) if r.get('type') == 'required_reviewers']
    if len(reviewers) != 1 or not reviewers[0].get('reviewers') or reviewers[0].get('prevent_self_review') is not True:
        raise ValueError('The publication environment requires independent reviewers and prevention of self-review')
    branch_policy = environment.get('deployment_branch_policy') or {}
    branches = policies.get('branch_policies', [])
    if (branch_policy.get('custom_branch_policies') is not True or branch_policy.get('protected_branches') is not False
            or len(branches) != 1 or branches[0].get('name') != 'main' or branches[0].get('type', 'branch') != 'branch'):
        raise ValueError('Publication environment must allow only the main branch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('tag', 'flavor', 'expected-source', 'actual-source'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--environment-json', required=True, type=Path)
    parser.add_argument('--branch-policies-json', required=True, type=Path)
    args = parser.parse_args()
    try:
        validate(args.tag, args.flavor, args.expected_source, args.actual_source)
        validate_environment(json.loads(args.environment_json.read_text(encoding='utf-8')),
                             json.loads(args.branch_policies_json.read_text(encoding='utf-8')))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print('Publication inputs and protected environment match the approved source and policy')


if __name__ == '__main__':
    main()
