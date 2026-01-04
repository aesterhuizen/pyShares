# Copilot Instructions for PyShares

## Project Overview
PyShares is a PyQt6-based GUI application for programmatic trading using the Robinhood API through the `robin-stocks` library. The app enables portfolio visualization, automated trading strategies, and real-time market data integration.

## Architecture Patterns

### Core Components
- **[app_main.py](app_main.py)**: Entry point - launches QApplication and MainWindow
- **[modules/MainWindow.py](modules/MainWindow.py)**: Core application logic (4600+ lines) containing all trading operations, UI interactions, and business logic
- **[modules/layout.py](modules/layout.py)**: Auto-generated UI layout from Qt Designer (DO NOT EDIT - regenerated from .ui file)
- **[modules/WorkerThread.py](modules/WorkerThread.py)**: Thread management for background operations (`CommandThread`, `UpdateThread`)
- **[modules/PopupWindows.py](modules/PopupWindows.py)**: Dialog classes for user interactions (`msgBoxGetCredentialFile`, `confirmMsgBox`)

### UI Development Workflow
- Design layouts in **[ui/AppLayout_splitter.ui](ui/AppLayout_splitter.ui)** using Qt Designer
- Regenerate **[modules/layout.py](modules/layout.py)** using `pyside6-uic` command: `pyside6-uic ui/AppLayout_splitter.ui -o modules/layout.py`
- NEVER edit layout.py directly - changes will be lost during regeneration
- Icons managed through **[icons/resources.qrc](icons/resources.qrc)** → **[modules/resources_rc.py](modules/resources_rc.py)**

### Environment & Authentication
- Configuration via `.env` files (see **[example.accInfo.env](example.accInfo.env)** for template)
- Stores env file path in `%LOCALAPPDATA%/pyShares/env_path.txt` for persistence
- Robinhood authentication uses username/password + TOTP MFA (`pyotp` library)
- Debug mode toggled via `debug=1/0` in env file

### Trading Operations Architecture
All trading functions follow consistent patterns in MainWindow.py:

```python
def [operation]_prev()    # Preview/calculation function
def [operation]()         # Actual execution with Robinhood API calls
```

**Core Trading Methods**:
- `sell_selected()` - Sell specific dollar amounts of selected stocks
- `sell_total_return_except_x()` - Sell gains except excluded stocks
- `buy_selected_with_x()` - Buy stocks with specified budget
- `reinvest_with_gains()` - Reinvest gains into selected stocks

**Trading Execution Pipeline**:
1. `Execute_operation()` - Validates inputs, shows confirmation dialog
2. `[method]_prev()` - Calculates preview data without API calls
3. `[method]()` - Executes trades via `robin-stocks` API in background thread

### Data Flow & State Management
- Portfolio data: `self.portfolio` dictionary updated via `get_stocks_from_portfolio()`
- Real-time updates: `UpdateThread` refreshes portfolio every 10 seconds
- UI state synchronization through extensive signal/slot connections
- Threading pattern: UI operations on main thread, API calls on worker threads

### Plotting & Visualization
- Matplotlib integration via custom `MpfCanvas` class for financial charts
- Three chart types: Gain/Loss bars, Sector-colored bars, Individual stock bars
- Chart data sourced from `yfinance` and portfolio calculations
- Automatic plot refresh on portfolio updates

## Development Commands

### Building
```bash
# Generate resources from icons
pyside6-rcc icons/resources.qrc -o modules/resources_rc.py

# Regenerate UI layout (CRITICAL - only way to update UI)
pyside6-uic ui/AppLayout_splitter.ui -o modules/layout.py

# Build executable
pyinstaller app_main.spec
```

### Running & Debugging
- Set `debug=1` in `.env` file to enable debug mode
- Debug mode shows full env file path in window title
- Terminal output via `ui.lstTerm` widget for operation logging
- All trading operations are bypassed when `debug=0` (safe mode)

## Critical Implementation Notes

### Thread Safety
- NEVER call Robinhood API from main thread
- All long-running operations use `CommandThread` or `UpdateThread`
- UI updates from worker threads must use Qt signals/slots

### Trading Safety
- All trades require user confirmation via `confirmMsgBox`
- Minimum share retention: 0.1 shares when selling
- Debug mode prevents actual trades (`os.environ['debug'] == '0'` for real trades)

### File I/O Patterns
- CSV format for stock lists: `symbol:quantity:price` per line
- Use `data_path = os.path.join(os.environ['LOCALAPPDATA'], "pyShares")` for app data
- Comprehensive error handling for file operations

### PyInstaller Considerations
- Resources bundled via `resources_rc.py` module
- Path resolution: Check `sys.frozen` for bundle vs development
- Exclude PyQt5 in spec file when using PySide6

When modifying this codebase:
1. Use Qt Designer for UI changes, then regenerate layout.py
2. Implement trading logic in preview functions first, then execution functions
3. Always test in debug mode before live trading
4. Follow the established signal/slot pattern for UI interactions
5. Use worker threads for any Robinhood API operations