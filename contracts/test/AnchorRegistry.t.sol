// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {SilentVerifyAnchorRegistry} from "../evm/SilentVerifyAnchorRegistry.sol";

contract AnchorRegistryTest is Test {
    SilentVerifyAnchorRegistry internal reg;

    function setUp() public {
        reg = new SilentVerifyAnchorRegistry();
    }

    function _loadPubkeyFp() internal view returns (bytes32 pk) {
        bytes memory raw = vm.readFileBinary("test/fixtures/pubkey_fp.bin");
        require(raw.length == 32, "bad pubkey_fp length");
        assembly {
            pk := mload(add(raw, 32))
        }
    }

    /// @dev Wire bytes are the exact UTF-8 JSON emitted by Python ``StateCertificate.to_json``.
    function test_postCommitmentOnly_keccak256_of_python_wire() public {
        bytes memory wire = bytes(vm.readFile("test/fixtures/state_cert_wire.json"));
        bytes32 wh = keccak256(wire);
        bytes32 pk = _loadPubkeyFp();

        reg.postCommitmentOnly(pk, wh, "pytest-export");

        bytes32 k = reg.anchorKey(pk, wh);
        assertGt(reg.anchoredAtBlock(k), 0);
    }

    function test_postFullWire_matches_commitment() public {
        bytes memory wire = bytes(vm.readFile("test/fixtures/state_cert_wire.json"));
        bytes32 wh = keccak256(wire);
        bytes32 pk = _loadPubkeyFp();

        reg.postFullWire(pk, wire, "full");
        bytes32 k = reg.anchorKey(pk, wh);
        assertGt(reg.anchoredAtBlock(k), 0);

        vm.expectRevert(bytes("SilentVerify: duplicate anchor"));
        reg.postCommitmentOnly(pk, wh, "dup");
    }
}
