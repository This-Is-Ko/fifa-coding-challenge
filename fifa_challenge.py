import math
import pandas as pd

# 1 Join both datasets such that each event is associated with the correct coordinates of the corresponding player at the given time
def load_event_and_tracking_data():
    events_df = pd.read_csv('events.csv')
    tracking_df = pd.read_csv('tracking.csv')

    # Prepare time data to match against tracking milliseconds
    # Match event time = 625.68 to equivalent t = 0
    # Convert time from seconds to milliseconds
    events_df['time'] = ((events_df['time'] - 625.68) * 1000).astype(int)
    tracking_df['t'] = tracking_df['t'].astype(int)

    # Handle ball position tracking
    # Replace events where player_id and team_id are null with ball id (-1)
    events_df['player_id'].fillna(-1, inplace=True)
    events_df['team_id'].fillna(-1, inplace=True)

    # Make id type consistent
    events_df['player_id'] = events_df['player_id'].astype(int)
    tracking_df['id_actor'] = tracking_df['id_actor'].astype(int)

    events_with_tracking_df = pd.merge_asof(events_df, tracking_df, left_by=['half_time', 'player_id'], right_by=['id_half', 'id_actor'], left_on='time', right_on='t', direction='backward')

    # Select required columns and ensure data is sorted
    events_with_tracking_df = events_with_tracking_df[['event_id', 'half_time', 'time', 'player_id', 'team_id', 'event', 'x', 'y']]
    events_with_tracking_df = events_with_tracking_df.sort_values(by='time')

    events_with_tracking_df.to_csv('events_with_tracking_data.csv', index=False)


# 2 Calculate the length of the ball trajectory from the initial kickoff to the first "Ball Out of Play" event
def calc_ball_trajectory_length():
    events_with_tracking_df = pd.read_csv('events_with_tracking_data.csv')
    
    # Data is in cm
    trajectory_length = 0.0
    previous_x, previous_y = None, None
    for index, row in events_with_tracking_df.iterrows():
        if row['event'] == 'Ball Out of Play':
            break

        x, y = row['x'], row['y']
        if previous_x is not None and previous_y is not None:
            trajectory_length += calculate_distance(previous_x, previous_y, x, y)

        previous_x, previous_y = x, y

    # Convert to meters
    trajectory_length_meters = trajectory_length/100
    print("Ball trajectory length from KO to first Ball Out of Play: {} meters".format(trajectory_length_meters))


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# 3 Add a new column to the first table that flags for each pass and cross event if the pass was successful or misplaced
def add_successful_pass_cross_flag():
    events_df = pd.read_csv('events.csv')
    events_df['pass_success'] = None

    for index, row in events_df.iterrows():
        if row['event'] in ['Pass', 'Cross']:
            # Get the next event entry
            next_event = events_df.iloc[index + 1] if index + 1 < len(events_df) else None

            # Check if the next event is 'Reception' from the same team
            if next_event is not None and next_event['event'] == 'Reception' and next_event['team_id'] == row['team_id']:
                events_df.at[index, 'pass_success'] = True
            else:
                events_df.at[index, 'pass_success'] = False

    events_df.to_csv('events_with_passing_success.csv', index=False)

# 4 Which player had the most passes, which had the best pass completion rate in percent
def calculate_passing_statistics():
    events_with_passing_success = pd.read_csv('events_with_passing_success.csv')

    pass_events = events_with_passing_success[events_with_passing_success['event'].isin(['Pass', 'Cross'])]

    # Find total passes by each player and highest pass count
    pass_counts = pass_events['player_id'].value_counts()
    most_passes_player = pass_counts.idxmax()

    # Find highest passing success percentage
    pass_completion_rates = pass_events.groupby('player_id')['pass_success'].mean().reset_index(name='pass_completion_rate')
    max_completion_rate = pass_completion_rates['pass_completion_rate'].max()
    # Find all players who match the highest percentage
    best_pass_completion_players = pass_completion_rates[pass_completion_rates['pass_completion_rate'] == max_completion_rate]['player_id']

    print("Most passes by: {}".format(most_passes_player))
    print("Best pass completion rate was {}% by: {}".format(max_completion_rate*100, list(best_pass_completion_players)))


if __name__ == '__main__':
    # 1
    load_event_and_tracking_data()
    # 2 - 78.66 meters
    calc_ball_trajectory_length()
    # 3 
    add_successful_pass_cross_flag()
    # 4 - Most passes by Player 289964
    #   - Multiple players had the best pass completion rate of 100%
    #     308352, 358112, 369744, 379955, 395433, 401281, 429392, 433806
    calculate_passing_statistics()