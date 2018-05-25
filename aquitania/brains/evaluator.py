########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||| #
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||| #
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||| #
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||| #
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||| #
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
########################################################################################################################

"""
.. moduleauthor:: H Roark

Evaluation methods were not as big of a priority as they should be, as I did very simplistic code just to get a few
quick results from the datasets that I was exploring.

Now, it is 30th of April of 2018, and I am making big improvements on the Strategy Evaluation side of things, and I am
doing at least a minimally informative version of strategy results.
"""

import pandas as pd

from aquitania.brains.statistics.util import *
from aquitania.execution.kelly import *
from aquitania.execution.monte_carlo import monte_carlo_bets


# TODO evaluate the possibility of not doing this as a class
class Evaluator:
    """
    The Evaluator class is used to make the necessary transformations in data to generate an output that will be able
    to evaluate automatically if a strategy is profitable or not and also give a visual output for humans to understand
    what kind of strategy they are dealing with.
    """

    def __init__(self, transformer):
        """
        Initializes the Evaluator.

        :param transformer: (IndicatorTransformer) use object that has already been instantiated with dataset params
        """
        # Initializes Variables
        self.transformer = transformer
        self.strategy_dicts = []  # Will be a list of dicts
        self.accuracy_metrics = [None, None]

    def kelly_adj_ratio(self, df_line, inverse):
        """
        Calculates Kelly Criterion Adjusted Ratio, using a 99CI interval for a Line of a DataFrame with specific data,
        such as columns 'count' and 'sum', and where name is the ratio.

        The adjusted ratio is half of the normal ratio, it is used to mitigate damage caused by incorrect evaluations.
        It doesn't have that big of an impact on profit depending on the chosen values.

        :param df_line: (DataFrame line) You should use apply(axis=1) on DataFrame that has the requirements above
        :param inverse: (bool) True if we are going to look at inverted trades (ratio_inverted_or_not)

        :return: Adjusted Kelly Criterion
        :rtype: int
        """
        # Get easy variable names
        n_trades, n_win_trades, ratio = df_line['count'], df_line['sum'], df_line.name[1]

        # Calculates 99 CI probability taking into account if it is a normal or inverted trade
        proba = ci_99_inverse_or_not(inverse, n_trades, n_win_trades)

        # Gets Ratio actual bracket value if its a normal or inverted trade
        ratio = self.ratio_inverted_or_not(inverse, ratio)

        # Calculates and returns the Adjusted Kelly Criterion
        return adjusted_kelly_criterion(ratio, proba)

    def evaluate_output(self, df, is_test):
        """
        Evaluates output from Indicators and from Artificial intelligence and generates a truth table to be traded based
        on the test set.

        Also generates statistics for humans to be able to evaluate and comprehend the kind of strategies they have in
        hand.

        :param df: (pandas DataFrame) containing Ratios and Probabilities by possible trade evaluated by AI

        :return: tuple of Truth tables to be traded, both for normal [0] and inverse [1] kind of trades
        :rtype: tuple of (2) DataFrames
        """
        # Sorts DataFrame
        df.sort_index(inplace=True)

        # Instantiate variables
        total_months = pd.to_timedelta([(df.index[-1] - df.index[0])]).astype('timedelta64[M]')[0]

        # Generate Kelly DataFrames
        k_df = self.generate_kelly_dataframe(df=df, inverse=False)
        ki_df = self.generate_kelly_dataframe(df=df, inverse=True)

        # Adds Kelly bet sizing to all trades DataFrame
        df = df.join(k_df[['kelly', 'kelly_coh']], on=['prediction_proba', 'ratio'], how='left')
        df = df.join(ki_df[['kelly', 'kelly_coh']], on=['prediction_proba', 'ratio_inverted'], how='left', rsuffix='_i')

        # Check for Kelly inconsistency error
        kelly_error(df)

        # Calculates Return Rate for all trades DataFrame
        df = self.df_return_rate(df)

        # Generates output for humans
        self.human_output_generation(df, k_df, ki_df, total_months, is_test)

        # Calculate accuracy metrics
        self.calc_results_metrics(df, is_test)

        # Returns tuple of DataFrames ([0] is not inverted, [1] is inverted)
        return k_df['kelly_coh'].unstack().fillna(0.0), ki_df['kelly_coh'].unstack().fillna(0.0)

    def human_output_generation(self, df, k_df, ki_df, total_months, is_test):
        """
        This method generates a human output in the console, and also creates the necessary files for running jupyter
        notebooks that generates visualizations relevant to the selected strategies.

        :param df: (DataFrame) with all trades and kelly values
        :param k_df: (DataFrame) with kelly values for normal trades
        :param ki_df: (DataFrame) with kelly values for inverted trades
        :param total_months: (int) number of months that are on the trading period
        :param is_test: (bool) True if is test set
        """
        # Generates Individual Strategy data (according to a unique bet sizing that depends on proba and ratio)
        k_df.apply(self.info_by_strategy, axis=1, args=(False, is_test))
        ki_df.apply(self.info_by_strategy, axis=1, args=(True, is_test))

        # Gets out of the loop if there is no Trade-Able strategy
        if len(self.strategy_dicts) == 0:
            no_tradable_strategies_message()
            return

        # Gets out of the loop if it is train set
        if not is_test:
            return

        # Save all trades DataFrame into disk
        df.to_csv('data/ai/all_trades.csv')

        # Creates a Strategy DataFrame to facilitate generation of other data
        st_df = pd.DataFrame(self.strategy_dicts)

        # Generates Total Number of Strategies (points in Kelly DataFrame which have bet sizing superior to 0)
        n_strategies = st_df.shape[0]

        # Get number of trades and winning trades
        n_trades, n_win_trades = st_df['n_trades'].sum(), st_df['n_win_trades'].sum()

        # Calculate for time periods
        n_trades_month = n_trades / total_months
        n_trades_year = n_trades_month * 12
        n_trades_week = n_trades_year / 52

        # Calculate probabilities
        raw_win_probability = n_win_trades / n_trades
        win_probability = lower_confidence_interval_99(n_win_trades, n_trades)

        # Calculate Mathematical Expectation per trade
        ev = multiple_expected_values(st_df['ratio'].values, st_df['n_win_trades'].values, st_df['n_trades'].values)

        # Calculate total returns and return per trade
        total_return = self.get_strategy_return()
        rate_of_return_per_trade = ((1 + total_return) ** (1 / n_trades)) - 1

        # Calculate time related returns
        yearly_returns = sorted_yearly_returns(df)
        monthly_rate_of_return = ((1 + total_return) ** (1 / total_months)) - 1
        yearly_rate_of_return = ((1 + monthly_rate_of_return) ** 12) - 1

        # Get best and worst years
        best_year = (pd.to_datetime(yearly_returns.index[-1]).year, yearly_returns[-1])
        worst_year = (pd.to_datetime(yearly_returns.index[0]).year, yearly_returns[0])

        # Makes a Monte Carlo rate of return calculations, and get brackets
        rr_monte_carlo = self.get_monte_carlo_strategy_return()
        quarter_1, quarter_2, quarter_3 = rr_monte_carlo[['25%', '50%', '75%']]

        # Set bold and end_bold variables
        bold, end_bold = '\033[1m', '\033[0m'

        # Prints text into console
        print('\n----------------------------------------------')
        print('{}COMBINATION OF ALL STRATEGIES{}'.format(bold, end_bold))
        print('----------------------------------------------')
        print('NUMBER OF STRATEGIES:          {0:.0f}'.format(n_strategies))
        print('TOTAL TRADES:                  {0:.0f}'.format(n_trades))
        print('TOTAL PROFITABLE TRADES:       {0:.0f}'.format(n_win_trades))
        print('% PROFITABLE TRADES:           {0:.2%}'.format(raw_win_probability))
        print('99% CI PROFITABLE TRADES:      {0:.2%}'.format(win_probability))
        print('MATHEMATICAL EXPECTATION:      {0:.2f}'.format(ev))
        print('TRADES BY WEEK:                {0:.2f}'.format(n_trades_week))
        print('TRADES BY MONTH:               {0:.2f}'.format(n_trades_month))
        print('TRADES BY YEAR:                {0:.2f}'.format(n_trades_year))
        print('TOTAL OF MONTHS:               {0:.0f}'.format(total_months))
        print('TOTAL RETURN:                  {0:.2%}'.format(total_return))
        print('YEARLY RATE OF RETURN:         {0:.2%}'.format(yearly_rate_of_return))
        print('BEST YEAR ({0:.0f}):              {1:.2%}'.format(best_year[0], best_year[1]))
        print('WORST YEAR ({0:.0f}):             {1:.2%}'.format(worst_year[0], worst_year[1]))
        print('MONTHLY RATE OF RETURN:        {0:.2%}'.format(monthly_rate_of_return))
        print('RATE OF RETURN PER TRADE:      {0:.2%}'.format(rate_of_return_per_trade))
        print('MONTE CARLO 25% TR:            {0:.2%}'.format(quarter_1))
        print('MONTE CARLO 50% TR:            {0:.2%}'.format(quarter_2))
        print('MONTE CARLO 75% TR:            {0:.2%}'.format(quarter_3))

    def info_by_strategy(self, df_line, inverse, is_test):
        """
        Evaluates every possible tradable point in the Kellys DataFrames, and creates an output for each one of them.

        :param df_line: (pandas DataFrame) line to be evaluated (from Kellys DataFrames)
        :param inverse: (bool) True if inverted trades
        :param is_test: (bool) True if is test set
        """
        # Initializes variables
        n_win_trades, n_trades, kel, bet_size = df_line['sum'], df_line['count'], df_line['kelly'], df_line['kelly_coh']

        # Check if there is an actual possible strategy
        if bet_size == 0:
            # If not, interrupt method
            return

        # Gets Ratio actual bracket value if its a normal or inverted trade
        ratio = self.ratio_inverted_or_not(inverse, df_line.name[1])

        # Calculates correct number of winning trades
        n_win_trades = n_trades - n_win_trades if inverse else n_win_trades

        # Creates and append a Strategy dicts to 'self.strategy_dicts' list
        st_dict = {'n_trades': n_trades, 'n_win_trades': n_win_trades, 'bet_sizing': bet_size, 'ratio': ratio,
                   'is_test': is_test}
        self.strategy_dicts.append(st_dict)

        # No need to print for train set
        if not is_test:
            return

        # Calculates 99 CI probability
        win_probability = lower_confidence_interval_99(n_win_trades, n_trades)

        # Calculates win probability
        raw_win_probability = n_win_trades / n_trades

        # Calculates rates of return
        rate_of_return = calculate_rate_of_return(bet_size, ratio, raw_win_probability)
        rate_of_return_99ci = calculate_rate_of_return(bet_size, ratio, win_probability)

        # Calculate Mathematical Expectation per trade
        exp_mat = expected_value(ratio, win_probability)

        # Sets values for 'bold' and 'end_bold'
        bold, end_bold = '\033[1m', '\033[0m'

        # Prints text into console
        print('\n-------------------------------------')
        print('{}STRATEGY #{}{}'.format(bold, len(self.strategy_dicts), end_bold))
        print('-------------------------------------')
        print('TOTAL TRADES:                 {0:.0f}'.format(n_trades))
        print('TOTAL PROFITABLE TRADES:      {0:.0f}'.format(n_win_trades))
        print('% PROFITABLE TRADES:          {0:.2%}'.format(raw_win_probability))
        print('99% CI PROFITABLE TRADES:     {0:.2%}'.format(win_probability))
        print('MATHEMATICAL EXPECTATION:     {0:.2f}'.format(exp_mat))
        print('WIN LOSS RATIO:               {0:.2f}'.format(ratio))
        print('BET SIZING:                   {0:.2%}'.format(bet_size))
        print('BET SIZING BEFORE COH:        {0:.2%}'.format(kel))
        print('RATE OF RETURN:               {0:.2%}'.format(rate_of_return))
        print('RATE OF RETURN 99% CI:        {0:.2%}'.format(rate_of_return_99ci))

    def get_strategy_return(self):
        """
        Calculates Strategy Return according to number of winning trades, total trades, bet sizing an ratio. Does not
        take into account a trade by trade calculation, so this won't enable us to know which year performed better
        for example.

        :return: Total Returns value
        :rtype: float
        """
        # Initializes variable
        balance = 1

        # Runs loop for each of the strategies in the 'self.strategy_dicts'
        for strategy in self.strategy_dicts:
            # Gets Variables
            n_trades, win_trades = strategy['n_trades'], strategy['n_win_trades']
            bet_sizing, ratio = strategy['bet_sizing'], strategy['ratio']

            # Makes a composite calculation of the balance
            balance *= trade_sequence_returns(n_trades, win_trades, bet_sizing, ratio)
        # Gets total returns (the '- 1' is used to discount the initial capital used)
        return balance - 1

    def get_monte_carlo_strategy_return(self, number_of_simulations=1000):
        """
        Calculates a lot of simulations (default=1000) using the Monte Carlo method, to give an idea of what are
        possibly likely outcomes.

        :return: Description of Aggregate Simulation values
        :rtype: pandas Series
        """
        # Initializes a Series object with the len of the number of simulations
        ser = pd.Series([1] * number_of_simulations)

        # Creates a simulation for each one of the strategy
        for strategy in self.strategy_dicts:
            # Gets Variables
            n_trades, win_trades = strategy['n_trades'], strategy['n_win_trades']
            bet_sizing, ratio = strategy['bet_sizing'], strategy['ratio']

            # Combines simulation results together
            ser = ser * monte_carlo_bets(win_trades / n_trades, bet_sizing, ratio, n_trades, number_of_simulations)

        # Discounts the initial capital
        ser = ser - 1

        # Returns a description of the Series object
        return ser.describe()

    def ratio_inverted_or_not(self, inverse, ratio):
        """
        Generates a ratio given a ratio bracket and a inverse dummy.

        :param inverse: (bool) True if inverted trade
        :param ratio: (int) ratio Bracket

        :return: Win/Loss Ratio
        :rtype: float
        """
        # If ratio 0, bracket would return -inf, which makes no practical sense, so we just return ratio = 0
        if ratio > 0:
            # Get correct ratio bin according to inverse or not
            return self.transformer.iratio_bins[ratio] if inverse is True else self.transformer.ratio_bins[ratio]
        else:
            # This will never be traded, as win loss ratio is 0, meaning that win value is 0
            return ratio

    def generate_kelly_dataframe(self, df, inverse):
        """
        Generates Kelly DataFrames, given if it is inverse or not.

        :param df: (pandas DataFrame) AI output DataFrame
        :param inverse: (boolean) True if inverted trade

        :return: DataFrame with bet sizing for each combination of ratio and proba
        :rtype: pandas DataFrame
        """
        # Gets ratio str
        ratio = 'ratio_inverted' if inverse else 'ratio'

        # Creates Kelly DataFrame
        k_df = df.groupby(['prediction_proba', ratio]).agg({'results': ['sum', 'count']})

        # Sets Kelly DataFrame columns
        k_df.columns = ['sum', 'count']

        # Sets 'kelly' column on DataFrame
        k_df['kelly'] = k_df.apply(self.kelly_adj_ratio, axis=1, args=(inverse,))

        # Creates empty DataFrame to make a sum with the current Kelly DataFrame
        ed = pd.DataFrame(0.0, range(0, self.transformer.n_ratio_bins), columns=range(0, self.transformer.n_proba_bins))

        # Checks for inconsistent columns (such as a higher probability yielding a lower bet size)
        k_df['kelly_coh'] = coherent_truth_table(ed + k_df['kelly'].unstack()).stack()

        # Returns Kelly DataFrame with FillNA = 0.0
        return k_df.fillna(0.0)

    def df_return_rate(self, df):
        """
        Calculate return rate for all trades DataFrame.

        This enables us to calculate things like return per specific year, best year, worst year.

        :param df: (pandas DataFrame) All trades DataFrame

        :return: All trades DataFrame with 'start_balance' and 'end_balance' columns for each row
        :rtype: pandas DataFrame
        """
        # Initializes variables
        balance = 1
        end_balances, start_balances = [], []

        # Runs calculations row by row
        for index, row in df.iterrows():
            # Get starting balance
            start_balances.append(balance)

            # Routine for normal trades
            if row['kelly_coh'] > 0 and row['ratio'] > 0:  # Check if ratio > 0 to avoid dealing with -inf

                # Winning Trade
                if row['results']:
                    balance *= (1 + (row['kelly_coh'] * self.transformer.ratio_bins[row['ratio']]))

                # Losing Trade
                else:
                    balance *= (1 - row['kelly_coh'])

            # Routine for inverted trades
            if row['kelly_coh_i'] > 0 and row['ratio_inverted'] > 0:  # Check if ratio > 0 to avoid dealing with -inf

                # Winning Trade
                if row['results']:
                    balance *= (1 + (row['kelly_coh_i'] * self.transformer.iratio_bins[row['ratio_inverted']]))

                # Losing Trade
                else:
                    balance *= (1 - row['kelly_coh_i'])

            # Get end balance
            end_balances.append(balance)

        # Sets new columns into DataFrame
        df['start_balance'], df['end_balance'] = start_balances, end_balances

        # Returns DataFrame with new columns
        return df

    def overfit_metrics(self):
        """
        Calculates overfit metrics.

        The idea here is to enable the human user to be able to assess whether the model is overfitting or not, and to
        give an idea of the extent of the overfitting.
        """
        # Initialize DataFrame with data from the strategies
        df = pd.DataFrame(self.strategy_dicts)

        # Initializes DataFrame with data from the accuracy metrics calculations
        df2 = pd.DataFrame(self.accuracy_metrics, index=[False, True])

        # Routine for when there is a valid train or test strategy
        try:
            # Creates a new DataFrame grouped by Train and Test sets
            gdf = df.groupby('is_test').agg({'n_trades': ['sum'], 'n_win_trades': ['sum', 'count']})

            # Set column names for DataFrame grouped by Train and Test sets
            gdf.columns = ['n_trades', 'n_win_trades', 'n_strategies']

            # Creates a new concatenated and transposed DataFrame
            ndf = pd.concat([gdf, df2], axis=1).T

            # Sets Column Names
            ndf.columns = ['Train Set', 'Test Set']

            # Runs routine to print overfitting metrics
            print_overfit_metrics(ndf)

        # Routine for when no valid strategy was found
        except:
            # Messages about the fact that no profitable strategies where found
            print('No Profitable Strategies Were Found in Train or Test Sets')

            # Gets the Transposed DataFrame
            df2 = df2.T

            # Get column names
            df2.columns = ['Train Set', 'Test Set']

            # Prints data not related to strategies
            print(df2)

    def calc_results_metrics(self, df, is_test):
        """
        Calculates metrics according to predictions probabilities and actual results.

        :param df: (pandas DataFrame) DataFrame with all trades
        :param is_test: (bool) True if it the test set

        :return: results metrics for comparison between predictions and actual outcomes
        :rtype: pandas DataFrame
        """
        pred = df['raw_predict']
        y = df['results']
        acc_dict = {'acc_proba': accuracy_proba(pred, y), 'acc_clf': accuracy_classifier(pred, y),
                    'prec_20': precision_metric(pred, y, 0.2, True), 'prec_25': precision_metric(pred, y, 0.25, True),
                    'prec_30': precision_metric(pred, y, 0.3, True), 'prec_35': precision_metric(pred, y, 0.35, True),
                    'prec_40': precision_metric(pred, y, 0.4, True), 'prec_45': precision_metric(pred, y, 0.45, True),
                    'prec_50<': precision_metric(pred, y, 0.5, True), 'prec_50>': precision_metric(pred, y, 0.5, False),
                    'prec_55': precision_metric(pred, y, 0.55, False), 'prec_60': precision_metric(pred, y, 0.6, False),
                    'prec_65': precision_metric(pred, y, 0.65, False), 'prec_70': precision_metric(pred, y, 0.7, False),
                    'prec_75': precision_metric(pred, y, 0.75, False), 'prec_80': precision_metric(pred, y, 0.8, False)}
        self.accuracy_metrics[
            is_test] = acc_dict


def coherent_truth_table(matrix_kelly):
    """
    Calculates a truth table for the Kelly DataFrame/Matrix that it is coherent with its close by values.

    It checks if there is a lower AI score being regarded as with a higher bet size, if so it caps this value to the
    higher AI score bet size.

    The same happens for the Ratio. (Although ratio might not be a strong inconsistency, I opted to make this control to
    avoid getting trapped in statistical anomalies).

    :param matrix_kelly: (pandas DataFrame) Kelly DataFrame/Matrix

    :return: coherent Kelly DataFrame
    :rtype: pandas DataFrame
    """
    # Creates a temporary DataFrame with shifted rows
    temp = matrix_kelly.shift(-1)

    # Save column names into a variable
    original_columns = matrix_kelly.columns

    # Rename temp DataFrame columns to make a numerical continuation of matrix_kelly numerical columns
    temp.columns = [column + len(matrix_kelly) for column in matrix_kelly.columns]

    # Concats horizontally matrix_kelly and temp
    matrix_kelly = pd.concat([matrix_kelly, temp], axis=1)

    # Runs loop until no further changes are made into Kelly DataFrame
    while True:
        # Creates a copy of matrix_kelly
        ndf = matrix_kelly.copy()

        # Apply bet sizing coherent method
        matrix_kelly = matrix_kelly.apply(bet_sizing_coherence, axis=1, args=(len(original_columns),))

        # If no changes are made exit loop
        if frame_equal(ndf, matrix_kelly):
            break

    # Returns selected columns
    return ndf[original_columns]


def bet_sizing_coherence(df_line, matrix_len):
    """
    Evaluates the bet sizing coherence of an altered Kelly DataFrame (doubled columns with shifted values).

    This method was made to be used on a DataFrame with '.apply()'.

    :param df_line: (pandas Series) which is a horizontal line of an altered Kelly DataFrame
    :param matrix_len: (int) original Kelly DataFrame length

    :return: returns a coherent bet sizing line
    :rtype: pandas Series
    """
    # Iterates row by row on the original Kelly DataFrame
    for i in range(0, matrix_len):
        # Check if current row has greater value than row below
        if df_line.values[i] > df_line.values[i + matrix_len]:
            # If it has, caps its value
            df_line.values[i] = df_line.values[i + matrix_len]
        if i > 0:
            # Check if row 'i-1' has greater value than row on the right
            if df_line.values[i - 1] > df_line.values[i]:
                # If it has, caps its value
                df_line.values[i - 1] = df_line.values[i]

    # Returns a coherent bet sizing line
    return df_line


def frame_equal(df1, df2):
    """
    Returns True if two DataFrames are equal.

    :param df1: (pandas DataFrame) to be compared
    :param df2: (pandas DataFrame) to be compared

    :return: True only if DataFrames are equal
    :rtype: bool
    """
    try:
        # Tries to assert Frames
        pd.testing.assert_frame_equal(df1, df2)

        # Doesn't throw error, DataFrames are equal
        return True

    except:
        # Throws error, DataFrames are not equal
        return False


def add_totals(df):
    """
    Creates a new row and a new column, stating what are the DataFrame subtotal values.

    It will be a new column in the right, that will have as value the sum of all other elements in the same row.

    :param df: (pandas DataFrame) to have subtotals in column and row to be added

    :return: DataFrame with subtotal column and row
    :rtype: pandas DataFrame
    """
    # Adds a new row with subtotals
    df.loc[len(df)] = [df[col].sum() for col in df.columns]

    # Adds a new column with subtotals
    df['TOTAL'] = [sum(row) for row in df.itertuples()]

    # Returns DataFrame with subtotal column and row
    return df


def kelly_error(df):
    """
    Throws error if a same trade is positive for both Kelly and Inverted Kelly.

    Having fixed exit points, that should be only possible if we work with negative spreads. Throwing an error here is a
    form to check if there is something very wrong with the code.

    :param df: (pandas DataFrame) All trades DataFrame already treated to include 'kelly' and 'kelly_i' columns
    """
    # Checks if there is a trade marked in the same line for 'kelly' and 'kelly_i'
    if df[(df['kelly'] > 0) & (df['kelly_i'] > 0)].shape[0] > 0:
        # In case there is, throws an error
        raise AssertionError('Results are impossible as of 30/04/2018 arch, check traceback and reevaluate code.')


def sorted_yearly_returns(df):
    """
    Gets an all trades DataFrame and generates yearly returns for it.

    :param df: (pandas DataFrame) all trades DataFrame with returns calculated line by line

    :return: Yearly returns
    :rtype: pandas DataFrame
    """
    # Calculates 'start_balance'
    start_balance = df.resample('Y')['start_balance'].head(1)

    # Calculates 'end_balance'
    end_balance = df.resample('Y')['end_balance'].tail(1)

    # Calculates yearly returns
    ser = pd.Series(end_balance.values / start_balance.values, index=end_balance.index).subtract(1)

    # Returns sorted values
    return ser.sort_values()


def no_tradable_strategies_message():
    """
    Prints in the console a message saying that there is no Tradable Strategies.
    """
    print('\n----------------------------------------------')
    print('AI FOUND NO TRADE-ABLE STRATEGIES')
    print('----------------------------------------------')


def accuracy_proba(predictions, y):
    """
    Returns accuracy metric using predictions probability.

    :param predictions: (np.array or pandas Series) Model predictions
    :param y: (np.array or pandas Series) actual results

    :return: metric that evaluates how close those predictions actually were
    :rtype: float
    """
    # TODO this metric might be better evaluated putting values together into brackets
    return 1 - (y - predictions).abs().mean()


def accuracy_classifier(predictions, y):
    """
    Returns accuracy metric using predictions. If prediction proba is 1 it will consider a winning trade, else it will
    consider as a losing trade.

    :param predictions: (np.array or pandas Series) Model predictions
    :param y: (np.array or pandas Series) actual results

    :return: metric that evaluates how close those predictions actually were
    :rtype: float
    """
    predictions = np.where(predictions >= 0.5, 1, 0)
    return accuracy_proba(predictions, y)


def precision_metric(predictions, y, threshold, inverted):
    """
    Calculates precision metric for trades.

    Gives a rough idea as to when it says it is likely to be a trade, how often it is in fact correct.

    This does not consider the particular bet sizing of a given trade, so it might have a lot of noise with trades of
    lowish probability but high payoff.

    :param predictions: (np.array or pandas Series) Model predictions
    :param y: (np.array or pandas Series) actual results
    :param threshold: probability score used to filter trades

    :return: metric that evaluates how often a perceived probability actually happens
    :rtype: float
    """
    # TODO add .count() to output
    if inverted:
        return 1 - y[predictions < threshold].mean()
    else:
        return y[predictions > threshold].mean()



def print_overfit_metrics(df):
    """
    Method used to print the OverFit metrics. It basically adds a title and prints a DataFrame.
    :param df: (pandas DataFrame) OverFit metrics DataFrame
    """
    print('\n\n----------------------------------------------')
    print('OVERFIT METRICS')
    print('----------------------------------------------')
    print(df)
