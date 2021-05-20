from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2shAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence, Locktime
from bitcoinutils.script import Script
from bitcoinutils.proxy import NodeProxy
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
import argparse
from decimal import Decimal
import sys
import requests


def main():
    # setup regtest network
    setup('regtest')
    # parsing arguments
    parser = argparse.ArgumentParser(description='Bitcoin Script for Task II')
    parser.add_argument('--private_key', help='Insert a public key')
    parser.add_argument('--time', type=int,
                        help='Insert a parameter (block height/Unix Epoch time that funds should be locked')
    parser.add_argument('--p2sh', help='Insert a p2sh')
    parser.add_argument('--p2pkh', help='Insert a p2pkh')
    args = parser.parse_args()

    priv = args.private_key
    absolute_param = args.time
    p2sh = args.p2sh
    p2pkh = args.p2pkh

    # set unlocking time
    if not absolute_param:
        print('error: You should add the time_lock')
        sys.exit(1)

    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, absolute_param)
    lock = Locktime(absolute_param)

    print('Connect with your RPC credentials')
    rpc_user = input('Enter rpc_username: ')
    rpcpassword = input('Enter rpc_password: ')

    # connect to NodeProxy with personal RPC credentials
    proxy = NodeProxy(rpc_user, rpcpassword).get_proxy()
    print(f'The blocks are {proxy.getblockcount()}')
    # Addresses emanate from private key
    p2pkh_sk = PrivateKey(priv)
    p2pkh_pk = p2pkh_sk.get_public_key().to_hex()
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()
    print(p2pkh_addr.to_string())

    from_addr = P2shAddress(p2sh)
    to_addr = P2pkhAddress(p2pkh)

    proxy.importaddress(from_addr.to_string(), "Absolute time_lock")
    unspent_txs = proxy.listunspent(0, 9999999, [from_addr.to_string()])
    print(unspent_txs)
    redeem_script = Script(
        [seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(),
         'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    list_tx_input = []
    total_amount = 0
    for i in unspent_txs:
        txin = TxInput(i['txid'], i['vout'], sequence=seq.for_input_sequence())
        list_tx_input.append(txin)
        total_amount = total_amount + i['amount']
    if total_amount == 0:
        sys.exit(0)

    response = requests.get("https://mempool.space/api/v1/fees/recommended")
    fee_per_byte = response.json()['fastestFee']
    print("Fastest fee per byte is : %d " % fee_per_byte)
    tx_size = len(list_tx_input) * 180 + 34 + 10 + len(list_tx_input)
    fees = tx_size * fee_per_byte / (10 ** 8)

    txout = TxOutput(to_satoshis(Decimal(total_amount) - Decimal(fees)), to_addr.to_script_pub_key())
    tx = Transaction(list_tx_input, [txout], lock.for_transaction())

    # print raw transaction
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    for i, txin in enumerate(list_tx_input):
        sig = p2pkh_sk.sign_input(tx, i, redeem_script)
        txin.script_sig = Script([sig, p2pkh_pk, redeem_script.to_hex()])

    # serialize the transaction
    signed_tx = tx.serialize()

    # test if the transaction will be accepted by the mempool
    res = proxy.testmempoolaccept([signed_tx])
    print(res)
    if not res[0]['allowed']:
        print("Transaction not valid")
        print(res)
        sys.exit(1)

    # print raw signed transaction ready to be broadcasted
    print("signed transaction:" + signed_tx)
    print("TxId:", tx.get_txid())
    proxy.sendrawtransaction(signed_tx)


if __name__ == "__main__":
    main()
