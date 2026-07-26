document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://localhost:8000'; // Assuming backend runs on port 8000

    // Collect Wallet Elements
    const walletAddressInput = document.getElementById('walletAddress');
    const collectWalletBtn = document.getElementById('collectWalletBtn');
    const collectWalletResultArea = document.getElementById('collectWalletResult');

    // System Status Elements
    const getStatusBtn = document.getElementById('getStatusBtn');
    const statusMarketSentiment = document.getElementById('statusMarketSentiment');
    const walletsContainer = document.getElementById('walletsContainer');

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

        collectWalletBtn.disabled = true;
        const originalText = collectWalletBtn.textContent;
        collectWalletBtn.textContent = 'Registering...';
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
        } finally {
            collectWalletBtn.disabled = false;
            collectWalletBtn.textContent = originalText;
        }
    });

    // --- Get System Status & Super Backpacks ---
    const updateSystemStatus = async (isManual = false) => {
        if (isManual) {
            getStatusBtn.disabled = true;
            getStatusBtn.textContent = 'Loading...';
        }
        try {
            const response = await fetch(`${apiUrl}/status`);
            const data = await response.json();

            if (response.ok) {
                // 1. Update Market Sentiment Badge
                const sentiment = data.market_sentiment || 'NEUTRAL';
                statusMarketSentiment.textContent = sentiment;
                statusMarketSentiment.className = `sentiment-badge ${sentiment}`;

                // 2. Clear previous wallets container
                walletsContainer.innerHTML = '';

                // 3. Render cards for each registered wallet
                if (data.wallets && data.wallets.length > 0) {
                    data.wallets.forEach(wallet => {
                        const card = document.createElement('div');
                        card.className = 'wallet-card';

                        const strategy = data.wallet_strategies[wallet] || 'N/A';
                        const scale = data.wallet_scaling_factors[wallet] || 1.0;
                        const backpack = data.wallet_backpacks[wallet] || { "USDC": 0, "SOL": 0, "JUP": 0, "PYTH": 0 };

                        // Assemble card HTML
                        let backpackHtml = '';
                        for (const [token, balance] of Object.entries(backpack)) {
                            backpackHtml += `
                                <div class="token-row">
                                    <span class="token-name">${token}</span>
                                    <span class="token-balance">${Number(balance).toFixed(4)}</span>
                                </div>
                            `;
                        }

                        card.innerHTML = `
                            <h4>${wallet}</h4>
                            <div class="wallet-meta">
                                <strong>Strategy:</strong> ${strategy}<br>
                                <strong>Scaling Factor:</strong> ${scale}x
                            </div>
                            <div class="backpack-inventory">
                                <h5>Super Backpack Assets</h5>
                                ${backpackHtml}
                            </div>
                        `;

                        walletsContainer.appendChild(card);
                    });
                } else {
                    walletsContainer.innerHTML = `
                        <p style="color: #666; font-style: italic; grid-column: 1 / -1;">
                            No wallets registered yet. Enter a wallet above to initiate the Billion Cycle simulation!
                        </p>
                    `;
                }
            } else {
                walletsContainer.innerHTML = `<p style="color: red;">Error: ${data.detail || response.statusText}</p>`;
            }
        } catch (error) {
            console.error('Get status error:', error);
            walletsContainer.innerHTML = `<p style="color: red;">Network error: ${error.message}</p>`;
        } finally {
            if (isManual) {
                getStatusBtn.disabled = false;
                getStatusBtn.textContent = 'Get System Status';
            }
        }
    };

    // Trigger on button click
    getStatusBtn.addEventListener('click', () => updateSystemStatus(true));

    // Auto-refresh the system status dashboard every 3 seconds to show live changes!
    setInterval(() => updateSystemStatus(false), 3000);
    // Fetch immediately on load
    updateSystemStatus(false);

    // --- Get Profit Events ---
    getProfitEventsBtn.addEventListener('click', async () => {
        const wallet = profitWalletAddressInput.value.trim();
        if (!wallet) {
            profitEventsResultArea.textContent = 'Please enter a wallet address.';
            return;
        }

        getProfitEventsBtn.disabled = true;
        const originalText = getProfitEventsBtn.textContent;
        getProfitEventsBtn.textContent = 'Fetching...';
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
        } finally {
            getProfitEventsBtn.disabled = false;
            getProfitEventsBtn.textContent = originalText;
        }
    });
});
