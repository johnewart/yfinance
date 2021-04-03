from yfinance import Ticker
from yfinance.ticker import OPTION_DATE_FORMAT
from yfinance.utils import merge_option_chains

from datetime import datetime
from pandas import DataFrame


def test_option_chains():
    ticker = Ticker("AAPL")
    dates = [str(x) for x in ticker.option_dates().keys()]
    assert len(dates) > 0
    first_date = datetime.strptime(dates[0], OPTION_DATE_FORMAT)
    assert first_date > datetime.today()

    options = ticker.option_chain(dates[0])
    assert options.calls is not None
    assert options.puts is not None

    merged_df: DataFrame = merge_option_chains([options])
    merged_calls = merged_df.query('optionType == "CALL"')
    merged_puts = merged_df.query('optionType == "PUT"')
    assert len(merged_calls) == len(options.calls)
    assert len(merged_puts) == len(options.puts)
    assert len(merged_df) == len(options.calls) + len(options.puts)


def test_options_between():
    ticker = Ticker("AAPL")
    dates = [str(x) for x in ticker.option_dates().keys()]
    assert len(dates) >= 3
    start_date = dates[1]
    end_date = dates[-1]
    assert start_date != end_date
    chains = ticker.options_between(start_date, end_date)
    assert len(chains) >= 2

    # Make sure our expirations are in the right range
    for chain in chains:
        call_df: DataFrame = chain.calls
        expiration_secs = call_df["expiration"][0].timestamp()
        expiration_date = datetime.utcfromtimestamp(expiration_secs).date()
        assert (
            expiration_date >= datetime.strptime(start_date, OPTION_DATE_FORMAT).date()
        )
        assert expiration_date <= datetime.strptime(end_date, OPTION_DATE_FORMAT).date()


def test_merged_chains():
    ticker = Ticker("AAPL")
    dates = [str(x) for x in ticker.option_dates().keys()]
    assert len(dates) >= 3
    start_date = dates[1]
    end_date = dates[-1]
    assert start_date != end_date
    chains = ticker.options_between(start_date, end_date)
    assert len(chains) >= 2
    merged_df = merge_option_chains(chains)
    # For every chain we received, make sure that we have
    for chain in chains:
        call_df: DataFrame = chain.calls
        expiration = call_df["expiration"][0]
        calls = merged_df[merged_df["expiration"] == expiration].query(
            'optionType == "CALL"'
        )
        assert len(calls) == len(call_df)
