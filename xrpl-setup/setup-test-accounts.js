const xrpl = require('xrpl')
const fs = require('fs')

async function setupTestAccounts() {
    console.log('Setting up XRPL test accounts...')

    const client = new xrpl.Client(process.env.XRPL_NODE)
    await client.connect()

    try {
        const platformWallet = xrpl.Wallet.generate()
        console.log('\nPlatform Management Wallet:')
        console.log('Address:', platformWallet.address)
        console.log('Seed:', platformWallet.seed)
        console.log('Public Key:', platformWallet.publicKey)

        const platformFund = await client.fundWallet(platformWallet)
        console.log('Platform Wallet Balance:', platformFund.balance, 'XRP')

        fs.writeFileSync('/data/platform-credentials.json', JSON.stringify({
            address: platformWallet.address,
            seed: platformWallet.seed,
            publicKey: platformWallet.publicKey,
            balance: platformFund.balance
        }, null, 2))

        console.log('\nCredentials saved to /data/platform-credentials.json')

    } catch (error) {
        console.error('Error setting up XRPL:', error)
        process.exit(1)
    } finally {
        await client.disconnect()
    }
}

setupTestAccounts().catch(console.error)
