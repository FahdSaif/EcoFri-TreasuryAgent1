// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract AIEnhancedWallet {
    address public owner;
    address public backupWallet;

    constructor(address _backupWallet) {
        owner = msg.sender;
        backupWallet = _backupWallet;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    function executeTransfer(address token, uint256 amount, address recipient) external onlyOwner {
        IERC20(token).transfer(recipient, amount);
    }

    function refillFromBackup(address token, uint256 amount) external onlyOwner {
        IERC20(token).transferFrom(backupWallet, address(this), amount);
    }

    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }
}
