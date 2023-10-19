# Load the dataset
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    return pd.read_csv('21-22.csv')

@st.cache_data
def load_playerstats():
    return pd.read_csv('playerstats.csv')

df = load_data()
playerstats_df = load_playerstats()

# Check if Streamlit's session state has a "page" attribute. If not, set it to "homepage"
if "page" not in st.session_state:
    st.session_state.page = "homepage"

# Function for the homepage
def homepage():
    # Displaying the details on the homepage
    st.title("NBA Player Shot Chart")
    st.write("Created by: Jason Chien(jc5858)")  # Replace [Your Name] with your name
    st.write("Course Title: Python for the MBAs")  # Replace [Course Title] with your course title
    st.write("""
    Introduction:
    This webapp provides a visual representation of NBA player shot charts. By selecting a team and player, users can view where shots were made or missed on the basketball court.
    """)

    st.write("""
    Instructions:
    1. Select a team from the dropdown list.
    2. After selecting a team, a list of players will be available. Select a player from this list.
    3. The shot chart for the selected player will be displayed. Missed shots are shown in red and made shots in green.
    """)

    # Button to proceed to the main app
    if st.button("Get Started"):
        st.session_state.page = "main_app"

# Function for the main app
def main_app():
    # Draw Court
    from matplotlib.patches import Circle, Rectangle, Arc
    def draw_court(ax=None, color='black', lw=2, outer_lines=False):
        # If an axes object isn't provided to plot onto, just get current one
        if ax is None:
            ax = plt.gca()

        # Create the basketball hoop
        hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

        # Create backboard
        backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

        # The paint
        # Create the outer box 0f the paint, width=16ft, height=19ft
        outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                            fill=False)
        # Create the inner box of the paint, widt=12ft, height=19ft
        inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                            fill=False)

        # Create free throw top arc
        top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                            linewidth=lw, color=color, fill=False)
        # Create free throw bottom arc
        bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                                linewidth=lw, color=color, linestyle='dashed')
        # Restricted Zone, it is an arc with 4ft radius from center of the hoop
        restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                        color=color)

        # Three point line
        # Create the side 3pt lines, they are 14ft long before they begin to arc
        corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                                color=color)
        corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
        # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
        # I just played around with the theta values until they lined up with the 
        # threes
        three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                        color=color)

        # Center Court
        center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color)
        center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                            linewidth=lw, color=color)

        # List of the court elements to be plotted onto the axes
        court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                        bottom_free_throw, restricted, corner_three_a,
                        corner_three_b, three_arc, center_outer_arc,
                        center_inner_arc]

        if outer_lines:
            # Draw the half court line, baseline and side out bound lines
            outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                    color=color, fill=False)
            court_elements.append(outer_lines)

        # Add the court elements onto the axes
        for element in court_elements:
            ax.add_patch(element)

        return ax

    # Sidebar for team selection
    unique_teams = sorted(df['TEAM_NAME'].unique())
    selected_team = st.sidebar.selectbox("Select a Team:", unique_teams)

    # Filter players based on the selected team and sort them
    team_players = sorted(df[df['TEAM_NAME'] == selected_team]['PLAYER_NAME'].unique())
    selected_player = st.sidebar.selectbox("Select a Player:", team_players)

    # Add a title for player's traditional stats
    st.title(f"{selected_player}'s Traditional Stats")

    # Extract the statistics for the selected player
    player_data = playerstats_df[playerstats_df['PLAYER_NAME'] == selected_player]

    # Columns to be adjusted
    adjust_columns = ['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']

    # Divide by the 'GP' value
    gp_value = player_data['GP'].values[0]
    for col in adjust_columns:
        player_data[col] = player_data[col] / gp_value

    # Extract the desired columns and their display names
    # Extract the desired columns and their display names
    columns = ['AGE', 'GP', 'FG_PCT', 'FG3_PCT', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']
    display_names = [
       "Age", "Game Played", "Field Goal Percentage",
      "3 Point Percentage", "Minutes Played", "Points", "Rebound", "Assist", "Steal", "Block", "Turnover"
    ]

    for col, display_name in zip(columns, display_names):
        value = player_data[col].values[0]
        st.write(f"{display_name}: {value:.2f}")  # Display values with two decimal places

    # Add a button for displaying the shot chart
    if st.button("Shot Chart"):
    
        # Plot setup
        player_df = df[df['PLAYER_NAME'] == selected_player]

        plt.figure(figsize=(12, 11))
        draw_court(outer_lines=True)
        title = f"Shot Chart for {selected_player}"
        plt.title(title)

        # Filter dataframe for "Missed Shot" and plot for the current player
        missed_shot = player_df[player_df['EVENT_TYPE'] == 'Missed Shot']
        plt.scatter(missed_shot.LOC_X, missed_shot.LOC_Y, s=15, c='red')

        # Filter dataframe for "Made Shot" and plot for the current player
        made_shot = player_df[player_df['EVENT_TYPE'] == 'Made Shot']
        plt.scatter(made_shot.LOC_X, made_shot.LOC_Y, s=15, c='green')

        plt.xlim(-300, 300)
        plt.ylim(-100, 500)

        # Display the plot in Streamlit
        st.pyplot(plt)  

# Control the flow: If session state is "homepage", show homepage, else show main app
if st.session_state.page == "homepage":
    homepage()
else:
    main_app()

#如何運行這個檔案, in anaconda prompt
#streamlit run python_final.py

