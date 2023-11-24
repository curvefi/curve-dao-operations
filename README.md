# Curve DAO Operations

This repository contains tools, written in python, for Curve DAO operations. The goal is to provide a simple command-line interface that allows veCRV holders to create and decode on-chain executable proposals, and simple scripts to produce analytics on governance in the Curve DAO.

Such a CLI tool allows independence from a web-ui: after all, decentralisation goes beyond just network decentralisation: it more or less means democratic access to technology.

# Who needs this?

veCRV holders looking to create on-chain proposals such as

- Creating or killing Curve DAO gauges that reward CRV inflation to addresses (liquidity pools or otherwise).
- Creating a smartwallet whitelist to lock veCRV (veCRV restricts smart contracts to lock CRV, subject to a DAO whitelist vote)
- Changing liquidity pool parameters
- Adding gauge types ...
- ... etc.

Curve DAO stakeholders have the ability to change the protocol in many ways. This repository is an attempt to consolidate all on-chain DAO operations into a single tool.

# Setup

## Environment Variables

Please setup access to IPFS using Infura at: [https://infura.io/](https://infura.io/)

1. `IPFS_PROJECT_ID`
2. `IPFS_PROJECT_SECRET`

Please setup access to Ethereum via Alchemy here: [https://www.alchemy.com/](https://www.alchemy.com/)

1. `WEB3_ALCHEMY_API_KEY`

If you're a power user that wants to use your own node, you'll need to setup `ape-config.yaml`:

```
hardhat:
  port: auto
  fork:
    ethereum:
      mainnet:
        upstream_provider: geth

geth:
  ethereum:
    mainnet:
      uri: <node url, e.g. http://localhost:9090>
```

## Installing the tool

The following is sufficient for installing all the dependencies (except one):

```
> python -m venv venv
> source ./venv/bin/activate
> pip install --upgrade pip
> pip install -r ./requirements.txt
```

The `ape-hardhat` plugin also requires `hardhat`, which should be npm installed using the `package-lock.json`:

```
npm install
```


# Available tools

Currently, the DAO operations tool grants the following:

#### `decode_executable`

This is a read-only tool that allows access to all users (they don't need to be a Curve Finance stakeholder) to decode an on-chain proposal.

Input args:

1. `vote_id`: The vote ID of an on-chain proposal

An example of its usage is show in the following:

```
$ ape run decode_executable decode --vote-type ownership --vote-id 223
```

Output:

```
Decoding VoteID: 223
Voting contract: 0xe478de485ad2fe566d49342cbd03e49ed7db3356 (ownership)
Call via agent: 0x40907540d8a6C65c637785e8f8B742ae6b0b9968
 ├─ To: 0x5a8fdC979ba9b6179916404414F7BA4D8B77C8A1
 ├─ Function: set_killed
 └─ Inputs:
    ├─ _gauge: 0x5AC6886Edd18ED0AD01C0B0910660637c551FBd6
    └─ _is_killed: True

Call via agent: 0x40907540d8a6C65c637785e8f8B742ae6b0b9968
 ├─ To: 0x2EF1Bc1961d3209E5743C91cd3fBfa0d08656bC3
 ├─ Function: set_killed
 └─ Inputs:
    ├─ _gauge: 0xdC69D4cB5b86388Fff0b51885677e258883534ae
    └─ _is_killed: True

Call via agent: 0x40907540d8a6C65c637785e8f8B742ae6b0b9968
 ├─ To: 0x2EF1Bc1961d3209E5743C91cd3fBfa0d08656bC3
 ├─ Function: set_killed
 └─ Inputs:
    ├─ _gauge: 0x16C2beE6f55dAB7F494dBa643fF52ef2D47FBA36
    └─ _is_killed: True

Results: Vote Passed (Execution Status: Executed)
├─ Voting Start Time: 2022-10-18 14:25:47
├─ Voting End Time: 2022-10-25 14:25:47
├─ Votes For: 260936423.49
├─ Votes Against: 0.0
├─ Support: 100.0% (Required: 51%)
└─ Quorum: 49.25% (Minimum: 30%)
```

# How to contribute:

The goal is to cover all DAO operations in CLI tools. All utility scripts go to: `scripts/utils`, and all CLI tools are stored in the `scripts` folder.

## Pre-commit

For linting, the repo uses pre-commit hooks. Please install and use them via:

```
> pre-commit install
> pre-commit run --all-files
```

In order to contribute, please fork off of the `main` branch and make your changes there. Your commit messages should detail why you made your change in addition to what you did (unless it is a tiny change).

If you need to pull in any changes from `main` after making your fork (for example, to resolve potential merge conflicts), please avoid using `git merge` and instead, `git rebase` your branch

Please also include sufficient test cases, and sufficient docstrings. All tests must pass before a pull request can be accepted into `main`.

# Disclaimer

This is experimental software and is provided on an "as is" and "as available" basis. We do not give any warranties and will not be liable for any loss incurred through any use of this codebase.
