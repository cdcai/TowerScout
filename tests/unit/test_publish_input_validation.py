"""Behavioral validation of dispatch-controlled publication inputs."""
import importlib.util
from copy import deepcopy
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('publish_inputs', ROOT / 'scripts/validate_publish_inputs.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SHA = 'a' * 40


@pytest.mark.parametrize('tag,flavor', [('v0.1.3','cpu'), ('v0.1.3-rc.1','cuda128'), ('v0.1.3-rc5-cpu','cpu'), ('v0.1.3-cuda128','cuda128')])
def test_versions_and_matching_flavors_are_accepted(tag, flavor):
    module.validate(tag, flavor, SHA, SHA)


@pytest.mark.parametrize('tag', ['latest', 'v1.2.3;touch injected', 'v1.2.3$(touch injected)', 'v1.2.3`id`', 'v1.2.3\nforged=value', '../v1.2.3', 'v1.2.3-cuda126', 'v１.2.3', 'v1.2.3 '])
def test_shell_and_nonversion_inputs_are_rejected(tag):
    with pytest.raises(ValueError):
        module.validate(tag, 'cpu', SHA, SHA)


@pytest.mark.parametrize('flavor,expected,actual', [('cuda128', SHA, 'b'*40), ('cpu', 'main', SHA), ('cpu', SHA.upper(), SHA), ('invalid',SHA,SHA)])
def test_unapproved_source_or_flavor_is_rejected(flavor, expected, actual):
    with pytest.raises(ValueError):
        module.validate('v1.2.3-cpu', flavor, expected, actual)


def _environment():
    return {'name': 'official-release',
            'protection_rules': [{'type': 'required_reviewers', 'prevent_self_review': True, 'reviewers': [{'type': 'User', 'reviewer': {'id': 1}}]}],
            'deployment_branch_policy': {'custom_branch_policies': True, 'protected_branches': False}}


def test_reviewed_main_only_environment_is_accepted():
    module.validate_environment(_environment(), {'branch_policies': [{'name': 'main', 'type': 'branch'}]})


@pytest.mark.parametrize('field,value', [('name','unprotected'), ('protection_rules',[]), ('deployment_branch_policy',None)])
def test_missing_or_weakened_environment_blocks_publication(field, value):
    environment = _environment()
    environment[field] = value
    with pytest.raises(ValueError):
        module.validate_environment(environment, {'branch_policies': [{'name': 'main', 'type': 'branch'}]})


@pytest.mark.parametrize('branches', [[], [{'name':'*','type':'branch'}], [{'name':'main','type':'tag'}], [{'name':'main','type':'branch'}, {'name':'other','type':'branch'}]])
def test_non_main_or_wildcard_environment_is_rejected(branches):
    with pytest.raises(ValueError):
        module.validate_environment(_environment(), {'branch_policies': branches})


def test_self_review_or_missing_reviewers_is_rejected():
    for field, value in [('prevent_self_review',False), ('reviewers',[])]:
        environment = deepcopy(_environment())
        environment['protection_rules'][0][field] = value
        with pytest.raises(ValueError):
            module.validate_environment(environment, {'branch_policies': [{'name':'main','type':'branch'}]})
