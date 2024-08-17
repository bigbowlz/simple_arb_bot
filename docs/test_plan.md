# Simple Arbitrage Bot Testing Plan
Testing will be conducted through three components: unit testing, functional testing, and strategy testing.

### Unit Testing
Unit testing for different data analysis and execution Python functions will be conducted using the testing framework **pytest**. 

### Functional Testing
Functional testing for smart contract execution will be conducted via E2E testing. Testnet trades will be populated through procedural transactions to simulate a competitive trading environment. The Simple Arb Bot is then used to monitor on-chain token prices and liquidity data, and execute trades when there is arbitrage opportunity.

Test Environment:
A local fork of the Ethereum mainnet state to the local test environment using Hardhat. This allows me to create a local blockchain instance that mirrors the current state of the Ethereum mainnet, enabling me to test in a realistic environment. The tricky part is that the fork cannot be a persistent state due to the limitations of the current testing tools, which requires me to have a procedural set up for contract creation and swap transactions to have deterministic states that I can build on top of.

Test Plan:
Module - Utilities 
	populate_routes.py
			get_contract_ABI(dex_contract): 
					1. successfully write to an ABI file for a UniswapV2Router
					2. successfully write to an ABI file for a PancakeSwapV2Router
					3. ABIs are in the configs directory
					4. ABI files are the same as on Etherscan (Sepolia)
			check_route(router1_address, router2_address, token1_address, token2_address):
					1. successfully check 2 valid routes and return True for both
					2. successfully check 2 invalid routes and return False for both
			populate_routes():
					1. successfully create routes in configs/sepolia.json
					2. successfully update routes in configs/sepolia.json
### Strategy Testing
Historical on-chain data will be used to conduct strategy testing (backtesting) to understand the performance of the trading strategy implemented in the Simple Arb Bot, and provide the basis for on-going strategy refinement. 

The project will also try to use deterministic procedurally generated transactions to test and optimize the performance of the strategy implemented.

Notes: focus on creating **different scenarios** in my scripts of procedural transaction population, instead of focusing on a realistic dynamic trading environment. Interactions based on 
1. different roles: regular traders; competing bots; liquidity movements from liquidity providers; whale traders; or,
2. different categories of interactions: trading; liquidity movements; *pool creation/deletion;*
(focusing on breadth so might have tradeoffs on the depth of the different scenarios; should list the limitations and future iteration plans of the implementation);
### Key Performance Metrics
The performance of the strategy is determined with the following four metrics.
1. **Profitability**
    - **Net Profit:** Calculate the total profits after deducting all costs, including transaction fees, gas fees, and any other operational costs. Net Profit = BalanceAfter - BalanceBefore.
    - **Return on Investment (ROI):** ROI = (Net Profit / Total Investment) * 100%. This measures the efficiency of the investment. Specifically, total investment refers to all liquidity provided to the arb contract as well as gas. In the actual implementation, as gas is supplied from a test account with unlimited ETH and is unable to factor in, it is omitted in the ROI calculation.
    - **Profit per Trade:** Average profit per arbitrage opportunity.
2. **Success Rate**
    - **Winning Trades vs. All Trades:** The ratio of profitable trades to all trades. Losing trades include both trades that execute on exchanges with a net loss, and trades that fail to execute on exchanges but incur gas costs.
3. **Execution Speed**
    - **Analysis Latency:** Time taken to detect and execute an arbitrage opportunity.  
    - **On-chain Execution Time:** The time between placing the order and the order getting executed, which reflects gas price competitiveness and serves gas optimization reference.
4. **Capital Utilization**
    - **Trade Volume:** The total volume of trades executed by the bot.
	- **Capital Efficiency (not included in demo):** Percentage of available capital actively used in arbitrage opportunities, calculated with averageLiquidity/totalLiquidity. This does not factor in gas. This metric is not included in the demo as the account balances are arbitrary due to a test environment.

**Performance Standard to add:**
Good values that I should be striving for; hard numbers;
Profitability: reference numbers;
Execution speed: no reference; 

Scoping!
