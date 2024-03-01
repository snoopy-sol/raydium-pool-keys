from solana.rpc.async_api import AsyncClient

from solders.pubkey import Pubkey

import time
from solana.rpc.commitment import Commitment

from utils.layouts import AMM_INFO_LAYOUT_V4_1
from utils.layouts import MARKET_LAYOUT
from utils.constants import RAY_AUTHORITY_V4, RAY_V4


# RPC_HTTPS_URL = "https://mainnet.helius-rpc.com/?api-key=aaaa-111-sss-cccc-dddd"


async def gen_pool(amm_id, ctx):


    try:
        amm_id = Pubkey.from_string(amm_id)

        # ctx = AsyncClient(RPC_HTTPS_URL, commitment="confirmed")

        start = time.time()
        while True:
            try:
                amm_data = (await ctx.get_account_info_json_parsed(amm_id)).value.data
                break
            except:
                if (time.time() - start) > 3:
                    return {"error" : "server timeout - took too long to find the pool info"}  
                pass

        amm_data_decoded = AMM_INFO_LAYOUT_V4_1.parse(amm_data)
        OPEN_BOOK_PROGRAM = Pubkey.from_bytes(amm_data_decoded.serumProgramId)
        marketId = Pubkey.from_bytes(amm_data_decoded.serumMarket)
        # print("Market --- ", str(marketId))
        try:
            while True:
                try:
                    marketInfo = (
                        await ctx.get_account_info_json_parsed(marketId)
                    ).value.data
                    break
                except:
                    if (time.time() - start) > 3:
                        return {"error" : "server timeout - took too long to find the pool info"} 
                    pass

            market_decoded = MARKET_LAYOUT.parse(marketInfo)


            pool_keys = {
                "amm_id": str(amm_id),
                "base_mint": str(Pubkey.from_bytes(market_decoded.base_mint)),
                "quote_mint": str(Pubkey.from_bytes(market_decoded.quote_mint)),
                "lp_mint": str(Pubkey.from_bytes(amm_data_decoded.lpMintAddress)),
                "version": 4,

                "base_decimals": amm_data_decoded.coinDecimals,
                "quote_decimals": amm_data_decoded.pcDecimals,
                "lpDecimals": amm_data_decoded.coinDecimals,
                "programId": str(RAY_V4),
                "authority": str(RAY_AUTHORITY_V4),

                "open_orders": str(Pubkey.from_bytes(amm_data_decoded.ammOpenOrders)),

                "target_orders": str(Pubkey.from_bytes(amm_data_decoded.ammTargetOrders)),


                "base_vault": str(Pubkey.from_bytes(amm_data_decoded.poolCoinTokenAccount)),
                "quote_vault": str(Pubkey.from_bytes(amm_data_decoded.poolPcTokenAccount)),

                "withdrawQueue": str(Pubkey.from_bytes(amm_data_decoded.poolWithdrawQueue)),
                "lpVault": str(Pubkey.from_bytes(amm_data_decoded.poolTempLpTokenAccount)),

                "marketProgramId": str(OPEN_BOOK_PROGRAM),
                "market_id": str(marketId),

                "market_authority": str(Pubkey.create_program_address(
                    [bytes(marketId)]
                    + [bytes([market_decoded.vault_signer_nonce])]
                    + [bytes(7)],
                    OPEN_BOOK_PROGRAM,
                )),

                "market_base_vault": str(Pubkey.from_bytes(market_decoded.base_vault)),
                "market_quote_vault": str(Pubkey.from_bytes(market_decoded.quote_vault)),
                "bids": str(Pubkey.from_bytes(market_decoded.bids)),
                "asks": str(Pubkey.from_bytes(market_decoded.asks)),
                "event_queue": str(Pubkey.from_bytes(market_decoded.event_queue)),
                "pool_open_time": amm_data_decoded.poolOpenTime
            }

            # print(f"End ms: {((time.time() - start)) * 1000}")

            # print(pool_keys)
            return pool_keys
        except:
            {"error" : "unexpected error occured"}
    except:
        return {"error" : "incorrect pair address"}