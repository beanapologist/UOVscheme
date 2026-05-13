// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.20;

/// @title SilentVerifyAnchorRegistry
/// @notice Cheap on-chain **posting** for SilentVerify wire objects (JSON / minified bytes).
///         Full UOV verification (`P(σ) = y`) is intentionally **off-chain** here: an EVM
///         implementation of the public map at NIST-scale parameters is a separate R&D track
///         (SNARK wrapper, optimized verifier, or threshold oracle). This contract gives you
///         two standard patterns: emit the full wire, or anchor only `keccak256(wire)`.
contract SilentVerifyAnchorRegistry {
    event CertificatePosted(
        bytes32 indexed wireHash,
        bytes32 indexed pubkeyFingerprint,
        address indexed submitter,
        bytes wire,
        string note
    );

    event CommitmentPosted(
        bytes32 indexed compositeKey,
        bytes32 indexed pubkeyFingerprint,
        address indexed submitter,
        bytes32 wireHash,
        string note
    );

    mapping(bytes32 => uint256) public anchoredAtBlock;

    function anchorKey(bytes32 pubkeyFp, bytes32 wireHash) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(pubkeyFp, wireHash));
    }

    /// @notice Emit full `wire` calldata (e.g. UTF-8 JSON). Off-chain indexers + verifiers consume it.
    function postFullWire(bytes32 pubkeyFp, bytes calldata wire, string calldata note) external {
        bytes32 wh = keccak256(wire);
        bytes32 k = anchorKey(pubkeyFp, wh);
        require(anchoredAtBlock[k] == 0, "SilentVerify: duplicate anchor");
        anchoredAtBlock[k] = block.number;
        emit CertificatePosted(wh, pubkeyFp, msg.sender, wire, note);
    }

    /// @notice Store only `keccak256(wire)`; distribute `wire` via IPFS, DA layer, or other L2 data.
    function postCommitmentOnly(bytes32 pubkeyFp, bytes32 wireHash, string calldata note) external {
        bytes32 k = anchorKey(pubkeyFp, wireHash);
        require(anchoredAtBlock[k] == 0, "SilentVerify: duplicate anchor");
        anchoredAtBlock[k] = block.number;
        emit CommitmentPosted(k, pubkeyFp, msg.sender, wireHash, note);
    }
}
