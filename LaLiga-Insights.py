#import libraries that are important for this project.
import streamlit as st
#we will be using pandas for data visualizations.
import pandas as pd
#we will also use plotly.
import plotly.express as px
import seaborn as sns
#use the read_csv function to read in the csv file containing our data.
df = pd.read_csv('C:/Users/17739/Documents/Streamlit/LaLiga_Stats.csv', header = 0)
#we can think about caching our data later - it helps with loading times.

#set the page config to configure width of app, logo, etc.
st.set_page_config(layout = 'wide', page_icon = 'laligalogo-removebg.png')

st.title('LaLiga Insights')
#calling dataframe allows us to load our table.
st.subheader('Key Statistics: ')
#st.dataframe(df)

#we can then start to code our sidebars.
#users can enter parameters that narrows down data displayed.

st.sidebar.header('User-Defined Parameters')
#first sidebar - choose a country to narrow down players
#note - we call multiselect after sidebar because we want the multiselect to be in sidebar.

#to make future work easier, we will rename columns with spaces in them because we can't refer to them if there are spaces in the names.
df.rename(columns = {'Yellow Cards': 'Yellow_Cards', 'Total Passes':'Total_Passes'}, inplace = True)
df.rename(columns = {'Time Played (min)': 'Time_Played_(min)', 'Fouls Conceded':'Fouls_Conceded'}, inplace = True)

#due to the "NONE" option for country, team, and position parameters, we create 3 new lists that do not contain that option.
#this is so the user will not be able to choose "NONE" for any of the parameters.
#we also remove the players with "NONE" data from the dataset.
countryList = df['Country'].unique()
countryList = np.delete(countryList, np.where(countryList == 'NONE')[0][0])

teamList = df['Team'].unique()
teamList = np.delete(teamList, np.where(teamList == 'NONE')[0][0])

posList = df['Position'].unique()
posList = np.delete(posList, np.where(posList == 'NONE')[0][0])


countryBar = st.sidebar.multiselect(
    "Country:",
    #first parameter is giving a label.
    #to specify the options, we can use the column titled "Country" in our dataframe.
    options = countryList,
    #the default can be set to all of the countries, showing all the players.
    default = countryList
)
#second sidebar - choose a team to narrow down players
teamBar = st.sidebar.multiselect(
    "Team:",
    options = teamList, 
    default = teamList
)
#third sidebar - choose a position to narrow down players.
positionBar = st.sidebar.multiselect(
    "Position:",
    options = posList,
    default = posList
)


#plug the sidebar to the dataframe
#we create a new dataframe variable to replace the older one.
#then use the query function to filter the data.
df_modified = df.query(
    "Country == @countryBar & Team == @teamBar & Position == @positionBar"
)

df_modified = df_modified.drop_duplicates()
df_modified = df_modified.drop(df_modified[df_modified['Country'] == 'NONE'].index, axis = 0)
df_modified = df_modified.drop(df_modified[df_modified['Team'] == 'NONE'].index, axis = 0)

###main page###

#if selection of the user is not in the dataframe, send a message to the user.
if df_modified.empty:
    st.warning("No data available based on your current filter settings. Change some filters to see data.")
    st.stop()
#calculate KPIs
#KPIs are key performance indicators that can summarize data
#some performance indicators of our dataset might include number of players, average number of appearances, most yellow cards,
#most touches, etc.

#stat 1: number of players: 
#we can use the shape method to find the number of players.
num_players = df_modified.shape[0]

#stat 2: avg # of appearances
avg_num_apps = int(df_modified['Appearances'].mean())

#stat 3: most yellow cards
most_yellow_cards = df_modified['Yellow_Cards'].max()

#display our data.
first_column, second_column, third_column = st.columns(3)

with first_column: 
    st.subheader('Number of Players:')
    st.subheader(num_players)
with second_column:
    st.subheader('Avg Number of Apps')
    st.subheader(avg_num_apps)
with third_column:
    st.subheader('Most Yellow Cards:')
    st.subheader(most_yellow_cards)
    st.write(df_modified['Yellow_Cards'].argmax())



st.subheader('Statistics By Player: ')
#shape is a tuple containing two elements - the number of rows and the number of columns.
#we can use that to create this sentence. It is a simple f string.
st.write(f"""Currently, there are {df_modified.shape[0]} rows and {df_modified.shape[1]} columns present.""")
#we can also include a link allowing user to download the CSV file we are using.

@st.cache_data
def convert_to_csv(df):
    #important - we need to use the @st.cache_data to prevent the computation from happening over and over again.
    #we must also encode the csv file returned for security.
    return df.to_csv(index = False).encode('utf-8')
csv = convert_to_csv(df_modified)
st.download_button(label = "Download data as CSV", file_name= "LaLiga_Stats.csv", data=csv, mime="text/csv")
st.dataframe(df_modified, use_container_width=False)

#add a divider to keep information separate and neat.
st.divider()
st.subheader('Graphical Display: ')
group_by_team_df = df_modified.groupby(by = 'Team').sum('Goals').reset_index().sort_values(by = 'Goals', ascending=False)
#st.dataframe(group_by_team_df)
#create bar chart showing goals per team.
goals_per_team = px.bar(
    #we can use streamlit's built in function to 
    #create the bar chart, but we can't specify titles there. So we can use plotly.
    group_by_team_df,
    x = 'Team',
    y = 'Goals',
    orientation = 'v',
    title = "<b>Goals Per Team</b>",
    template="plotly_white"
)

#second chart: pie chart showing goals scored by country
#we don't have a specific column for this, so we have to group a couple of columns and assign this to a new dataset.
group_by_country_df = df_modified.groupby(by ='Country').sum('Goals').reset_index().sort_values(by = 'Goals', ascending=False)

#we can drop the rows where the number of goals is 0, to keep the pie chart clean.
#st.dataframe(group_by_country_df)
group_by_country_df = group_by_country_df.drop(group_by_country_df[group_by_country_df['Goals'] < 10].index, axis = 0)
goals_by_country = px.pie(
    group_by_country_df, 
    values = 'Goals',
    names = 'Country',
    title = '<b>Distribution of Goals By Country</b>'
)

goals_per_team.update_traces(marker_color = '#7639bf')
left_column, right_column = st.columns(2)
left_column.plotly_chart(goals_per_team, use_container_width=True)
right_column.plotly_chart(goals_by_country, use_container_width=True)

st.divider()

#third graph: horizontal bar chart showing number of fouls conceded by different positions.
group_by_fouls_df = df_modified.groupby('Position').sum("Fouls_Conceded").reset_index().sort_values(ascending=False, by="Fouls_Conceded")
#st.dataframe(group_by_fouls_df)
position_vs_fouls = px.bar(
    group_by_fouls_df,
    x = 'Fouls_Conceded',
    y = 'Position', 
    orientation = "h",
    title = '<b>Fouls Conceded Per Position</b>'
)

#use the update_traces method to change the bar colors.
position_vs_fouls.update_traces(marker_color = '#f54040')
st.plotly_chart(position_vs_fouls, use_container_width = True)
st.divider()
#fourth graph: create a heatmap of some sort.
#use plotly to create heatmap, using imshow function.
#set img to the data being displayed - in this case, the correlation matrix returned from df_for_heatmap.corr().

df_for_heatmap = df_modified.drop(['Name', 'Country', 'Position', 'Team'], axis = 1, inplace = False)

heatmap = px.imshow(
    img = df_for_heatmap.corr(), 
    #allows us to show values.
    text_auto= True,
    aspect = 'auto',
    title= '<b>Correlation Matrix Heatmap: </b>'
)
st.plotly_chart(heatmap, use_container_width=True)

























