document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://localhost:8000'; // Assuming backend runs on port 8000

    // Collect Wallet Elements
    const collectWalletForm = document.getElementById('collectWalletForm');
    const walletAddressInput = document.getElementById('walletAddress');
    const collectWalletBtn = document.getElementById('collectWalletBtn');
    const collectWalletResultArea = document.getElementById('collectWalletResult');

    // System Status Elements
    const getStatusBtn = document.getElementById('getStatusBtn');
    const walletsListUl = document.getElementById('walletsList');
    const scalingFactorsDataPre = document.getElementById('scalingFactorsData');
    const strategiesDataPre = document.getElementById('strategiesData');
    const autoRefreshCb = document.getElementById('autoRefreshCb');

    let autoRefreshInterval = null;

    // Profit Events Elements
    const profitEventsForm = document.getElementById('profitEventsForm');
    const profitWalletAddressInput = document.getElementById('profitWalletAddress');
    const getProfitEventsBtn = document.getElementById('getProfitEventsBtn');
    const profitEventsResultArea = document.getElementById('profitEventsResult');

    // Helpers to manage button states
    const setButtonLoading = (btn, text, isLoading) => {
        btn.disabled = isLoading;
        if (isLoading) {
            btn.dataset.originalText = btn.textContent;
            btn.textContent = text;
        } else {
            btn.textContent = btn.dataset.originalText || btn.textContent;
        }
    };

    // Helper to validate and style inputs dynamically
    const setupInputValidation = (input, form) => {
        input.addEventListener('input', () => {
            if (input.value.trim()) {
                input.removeAttribute('aria-invalid');
                input.classList.remove('invalid-input');
            }
        });
    };

    setupInputValidation(walletAddressInput);
    setupInputValidation(profitWalletAddressInput);

    // --- Collect Wallet ---
    collectWalletForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const wallet = walletAddressInput.value.trim();
        if (!wallet) {
            walletAddressInput.setAttribute('aria-invalid', 'true');
            walletAddressInput.classList.add('invalid-input');
            collectWalletResultArea.textContent = 'Please enter a wallet address.';
            walletAddressInput.focus();
            return;
        }

        walletAddressInput.removeAttribute('aria-invalid');
        walletAddressInput.classList.remove('invalid-input');
        collectWalletResultArea.textContent = 'Registering...';
        setButtonLoading(collectWalletBtn, 'Registering...', true);
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
            setButtonLoading(collectWalletBtn, '', false);
        }
    });

    // --- Get System Status ---
    const fetchStatus = async (isAutoRefresh = false) => {
        if (!isAutoRefresh) {
            walletsListUl.innerHTML = '';
            const loadingLi = document.createElement('li');
            loadingLi.textContent = 'Loading...';
            walletsListUl.appendChild(loadingLi);

            scalingFactorsDataPre.textContent = 'Loading...';
            strategiesDataPre.textContent = 'Loading...';
            setButtonLoading(getStatusBtn, 'Loading...', true);
        }
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
                    const noWalletsLi = document.createElement('li');
                    noWalletsLi.textContent = 'No wallets registered.';
                    walletsListUl.appendChild(noWalletsLi);
                }

                // Scaling Factors
                scalingFactorsDataPre.textContent = JSON.stringify(data.wallet_scaling_factors || {}, null, 2);

                // Strategies
                strategiesDataPre.textContent = JSON.stringify(data.wallet_strategies || {}, null, 2);

            } else {
                if (!isAutoRefresh) {
                    walletsListUl.innerHTML = '';
                    const errorLi = document.createElement('li');
                    errorLi.textContent = `Error loading wallets: ${data.detail || response.statusText}`;
                    walletsListUl.appendChild(errorLi);

                    scalingFactorsDataPre.textContent = `Error: ${data.detail || response.statusText}`;
                    strategiesDataPre.textContent = `Error: ${data.detail || response.statusText}`;
                }
            }
        } catch (error) {
            console.error('Get status error:', error);
            if (!isAutoRefresh) {
                walletsListUl.innerHTML = '';
                const errorLi = document.createElement('li');
                errorLi.textContent = `Network error: ${error.message}`;
                walletsListUl.appendChild(errorLi);

                scalingFactorsDataPre.textContent = `Network error: ${error.message}`;
                strategiesDataPre.textContent = `Network error: ${error.message}`;
            }
        } finally {
            if (!isAutoRefresh) {
                setButtonLoading(getStatusBtn, '', false);
            }
        }
    };

    getStatusBtn.addEventListener('click', () => fetchStatus(false));

    // Handle Auto-Refresh
    const toggleAutoRefresh = () => {
        if (autoRefreshCb.checked) {
            // Trigger immediately first, then start interval
            fetchStatus(true);
            autoRefreshInterval = setInterval(() => {
                fetchStatus(true);
            }, 5000);
        } else {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
            }
        }
    };

    autoRefreshCb.addEventListener('change', toggleAutoRefresh);

    // Clean up interval on page unload/unmount safely
    window.addEventListener('beforeunload', () => {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    });

    // --- Get Profit Events ---
    profitEventsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const wallet = profitWalletAddressInput.value.trim();
        if (!wallet) {
            profitWalletAddressInput.setAttribute('aria-invalid', 'true');
            profitWalletAddressInput.classList.add('invalid-input');
            profitEventsResultArea.textContent = 'Please enter a wallet address.';
            profitWalletAddressInput.focus();
            return;
        }

        profitWalletAddressInput.removeAttribute('aria-invalid');
        profitWalletAddressInput.classList.remove('invalid-input');
        profitEventsResultArea.textContent = 'Fetching profit events...';
        setButtonLoading(getProfitEventsBtn, 'Fetching...', true);
        try {
            const response = await fetch(`${apiUrl}/profit_events?wallet=${encodeURIComponent(wallet)}`);
            const data = await response.json();
            if (response.ok) {
                profitEventsResultArea.textContent = ''; // clear text
                if (data.profitEvents && data.profitEvents.length > 0) {
                    const ul = document.createElement('ul');
                    data.profitEvents.forEach(event => {
                        const li = document.createElement('li');
                        li.textContent = `ID: ${event.id}, Amount: ${event.amount}, Sent: ${event.sent}`;
                        ul.appendChild(li);
                    });
                    profitEventsResultArea.appendChild(ul);
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
            setButtonLoading(getProfitEventsBtn, '', false);
        }
    });
});
