document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://localhost:8000'; // Assuming backend runs on port 8000

    // Collect Wallet Elements
    const walletAddressInput = document.getElementById('walletAddress');
    const collectWalletBtn = document.getElementById('collectWalletBtn');
    const collectWalletResultArea = document.getElementById('collectWalletResult');

    // System Status Elements
    const getStatusBtn = document.getElementById('getStatusBtn');
    const walletsListUl = document.getElementById('walletsList');
    const scalingFactorsDataPre = document.getElementById('scalingFactorsData');
    const strategiesDataPre = document.getElementById('strategiesData');

    // Profit Events Elements
    const profitWalletAddressInput = document.getElementById('profitWalletAddress');
    const getProfitEventsBtn = document.getElementById('getProfitEventsBtn');
    const profitEventsResultArea = document.getElementById('profitEventsResult');

    // --- Collect Wallet ---
    collectWalletBtn.addEventListener('click', async () => {
        const wallet = walletAddressInput.value.trim();
        if (!wallet) {
            collectWalletResultArea.textContent = 'Please enter a wallet address.';
            return;
        }
        collectWalletResultArea.textContent = 'Registering...';
        try {
            const response = await fetch(`${apiUrl}/collect_wallet`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wallet: wallet })
            });
            const data = await response.json();
            if (response.ok) {
                collectWalletResultArea.textContent = `Wallet ${data.wallet} status: ${data.status}, Strategy: ${data.strategy}`;
            } else {
                collectWalletResultArea.textContent = `Error: ${data.detail || response.statusText}`;
            }
        } catch (error) {
            console.error('Collect wallet error:', error);
            collectWalletResultArea.textContent = `Network error: ${error.message}`;
        }
    });

    // --- Get System Status ---
    getStatusBtn.addEventListener('click', async () => {
        walletsListUl.innerHTML = '<li>Loading...</li>'; // Clear previous before loading
        scalingFactorsDataPre.textContent = 'Loading...';
        strategiesDataPre.textContent = 'Loading...';
        try {
            const response = await fetch(`${apiUrl}/status`);
            const data = await response.json();

            if (response.ok) {
                // Wallets List
                walletsListUl.innerHTML = ''; // Clear loading/previous
                if (data.wallets && data.wallets.length > 0) {
                    data.wallets.forEach(wallet => {
                        const li = document.createElement('li');
                        li.textContent = wallet;
                        walletsListUl.appendChild(li);
                    });
                } else {
                    walletsListUl.innerHTML = '<li>No wallets registered.</li>';
                }

                // Scaling Factors
                scalingFactorsDataPre.textContent = JSON.stringify(data.wallet_scaling_factors || {}, null, 2);

                // Strategies
                strategiesDataPre.textContent = JSON.stringify(data.wallet_strategies || {}, null, 2);

            } else {
                walletsListUl.innerHTML = `<li>Error loading wallets: ${data.detail || response.statusText}</li>`;
                scalingFactorsDataPre.textContent = `Error: ${data.detail || response.statusText}`;
                strategiesDataPre.textContent = `Error: ${data.detail || response.statusText}`;
            }
        } catch (error) {
            console.error('Get status error:', error);
            walletsListUl.innerHTML = `<li>Network error: ${error.message}</li>`;
            scalingFactorsDataPre.textContent = `Network error: ${error.message}`;
            strategiesDataPre.textContent = `Network error: ${error.message}`;
        }
    });

    // --- Get Profit Events ---
    getProfitEventsBtn.addEventListener('click', async () => {
        const wallet = profitWalletAddressInput.value.trim();
        if (!wallet) {
            profitEventsResultArea.textContent = 'Please enter a wallet address.';
            return;
        }
        profitEventsResultArea.textContent = 'Fetching profit events...';
        try {
            const response = await fetch(`${apiUrl}/profit_events?wallet=${encodeURIComponent(wallet)}`);
            const data = await response.json();
            if (response.ok) {
                if (data.profitEvents && data.profitEvents.length > 0) {
                    let html = '<ul>';
                    data.profitEvents.forEach(event => {
                        html += `<li>ID: ${event.id}, Amount: ${event.amount}, Sent: ${event.sent}</li>`;
                    });
                    html += '</ul>';
                    profitEventsResultArea.innerHTML = html;
                } else {
                    profitEventsResultArea.textContent = 'No profit events found for this wallet.';
                }
            } else {
                profitEventsResultArea.textContent = `Error: ${data.detail || response.statusText}`;
            }
        } catch (error) {
            console.error('Get profit events error:', error);
            profitEventsResultArea.textContent = `Network error: ${error.message}`;
        }
    });
});
