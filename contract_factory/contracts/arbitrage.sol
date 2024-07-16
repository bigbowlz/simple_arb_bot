// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Arbitrage {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function executeTrade(
        address _router1,
        address _router2,
        address _token1,
        address _token2,
        uint256 _amount
    ) external onlyOwner {  
        uint256 initialBalance = getBalance(_token1);
        uint256 initialBalanceToken2 = getBalance(_token2);

        swap(_router1, _token1, _token2, _amount);
        uint256 tradeReturn = getBalance(_token2) - initialBalanceToken2;
        
        swap(_router2, _token2, _token1, tradeReturn);
        require(getBalance(_token1) > initialBalance, "Trade reverted. Failed to profit.");
    }

    function estimateTradeReturn(
        address _router1,
        address _router2,
        address _token1,
        address _token2,
        uint256 _amount
    ) external view returns (uint256) {
        uint256 amountOut1 = IUniswapV2Router02(_router1).getAmountsOut(_amount, getPathForTokenToToken(_token1, _token2))[1];
        uint256 amountOut2 = IUniswapV2Router02(_router2).getAmountsOut(amountOut1, getPathForTokenToToken(_token2, _token1))[1];
        return amountOut2;
    }

    function getBalance(address _tokenContractAddress) public view returns (uint256) {
        return IERC20(_tokenContractAddress).balanceOf(address(this));
    }

    function withdrawToken(address _tokenAddress) external onlyOwner {
        uint256 balance = IERC20(_tokenAddress).balanceOf(address(this));
        require(balance > 0, "No tokens to withdraw");
        IERC20(_tokenAddress).transfer(owner, balance);
    }

    function withdrawETH() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No ETH to withdraw");
        payable(owner).transfer(balance);
    }

    function swap(
        address _router,
        address _tokenIn,
        address _tokenOut,
        uint256 _amount
    ) internal {
        IERC20(_tokenIn).approve(_router, _amount);
        address[] memory path = getPathForTokenToToken(_tokenIn, _tokenOut);
        IUniswapV2Router02(_router).swapExactTokensForTokens(
            _amount,
            1, // Accept any amount of tokens out
            path,
            address(this),
            block.timestamp + 60 // Set a 1 min deadline to the swap transaction against front-running.
        );
    }

    function getPathForTokenToToken(address _tokenIn, address _tokenOut) internal pure returns (address[] memory) {
        address[] memory path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;
        return path;
    }

    // Function to receive ETH when `msg.data` is empty
    receive() external payable {}
    
    // Function to receive ETH when `msg.data` is not empty
    fallback() external payable {}
}
