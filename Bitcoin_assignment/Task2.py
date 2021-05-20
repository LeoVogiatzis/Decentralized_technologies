from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2shAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
# rpcuser=Alice
# rpcpassword=DONT_USE_THIS_YOU_WILL_GET_ROBBED_8ak1gI25KFTvjovL3gAM967mies3E=
import argparse
from decimal import Decimal


def main():
    # setup regtest network
    setup('regtest')
    # parsing arguments
    # parser = argparse.ArgumentParser(description='Bitcoin Script for Task II')
    # parser.add_argument('-private_key', help='Insert a public key')
    # parser.add_argument('--time_loc', type=int,
    #                     help='Insert a parameter (block height/Unix Epoch time that funds should be locked')
    # parser.add_argument('-p2sh', help='Insert a p2sh')
    # parser.add_argument('-p2pkh', help='Insert a p2pkh')
    # args = parser.parse_args()
    #
    # priv = args.private_key
    # absolute_param = args.time_loc
    # p2sh = args.time_loc
    # p2pkh = args.p2pkh
    #

    # print('Connect with your RPC credentials')
    # rpc_user = input('Enter rpc_username:')
    # rpcpassword = input('Enter rpc_password')

    # connect to NodeProxy with personal RPC credentials
    # proxy = NodeProxy(rpc_user, rpcpassword).get_proxy()
    # list = proxy.listunspent(minconf, maxconf, "[\"addr\"]")

    # calculate the amount of bitcoins to send
    # btc_to_send = sum(map(lambda x: int(x['amount']), json.loads(list)))
    # testing
    proxy = NodeProxy('alice', 'DONT_USE_THIS_YOU_WILL_GET_ROBBED_8ak1gI25KFTvjovL3gAM967mies3E=').get_proxy()
    print(proxy.getblockcount())
    # 'cVRDWtKS3J7ZUqAuECMWJc7RhQcRAwqvQWR1n6KetZck5o9tepTL'
    # the key that corresponds to the P2WPKH address
    p2pkh_sk = PrivateKey('cPHoz48mhLh2sjtYtArwsvPVuxMkQWySJ9HVeTJsLbFEKbppkTvQ')
    p2pkh_pk = p2pkh_sk.get_public_key()
    p2pkh_addr = p2pkh_pk.get_address()
    print(p2pkh_addr.to_string())

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, 10)
    redeem_script = Script(
        [seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(),
         'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    p2sh_addr = P2shAddress.from_script(redeem_script)
    print(proxy.list_unspent(0, 9999999, p2sh_addr))

    x=1

    # End Testing
    proxy.list_unspent(p2sh)

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, absolute_param)
    # the p2sh script and the corresponding address
    redeem_script = Script(
        [seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(),
         'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    p2sh_addr = P2shAddress.from_script(redeem_script)

    # create transaction input from tx id of UTXO (contained 11.1 tBTC)
    txin = TxInput(txid, vout=0, sequence=seq.for_input_sequence())
    # the UTXO of the P2SH-P2WPKH that we are trying to spend
    # inp = TxInput('95c5cac558a8b47436a3306ba300c8d7af4cd1d1523d35da3874153c66d99b09', 0)


    # the address to send funds to
    # to_addr = P2pkhAddress('mvBGdiYC8jLumpJ142ghePYuY8kecQgeqS')

    # the output sending 0.001 -- 0.0004 goes to miners as fee -- no change
    txout = TxOutput(to_satoshis(0.001), p2pkh.to_script_pub_key())

    # create a tx with at least one segwit input
    tx = Transaction([txin], [txout], has_segwit=True)

    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # use the private key corresponding to the address that contains the
    # UTXO we are trying to spend to create the signature for the txin -
    # note that the redeem script is passed to replace the scriptSig
    sig = priv.sign_input(tx, 0, redeem_script)
    # print(sig)

    # set the scriptSig (unlocking script) -- unlock the P2PKH (sig, pk) plus
    # the redeem script, since it is a P2SH
    txin.script_sig = Script([sig, priv.get_public_key().to_hex(), redeem_script.to_hex()])
    signed_tx = tx.serialize()

    # print raw signed transaction ready to be broadcasted
    print("\nRaw signed transaction:\n" + signed_tx)
    print("\nTxId:", tx.get_txid())


if __name__ == "__main__":
    main()