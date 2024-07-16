// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract BTC_iCAN is ERC20 {
    constructor(uint256 initialSupply) ERC20("BTC iCAN", "BTC") {
        _mint(msg.sender, initialSupply);
    }
    
    function decimals() public view virtual override returns (uint8) {
        return 8;
    }
}