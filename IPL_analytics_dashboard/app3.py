import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="IPL Analytics Hub",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to right, #1e1e2f, #252540); color: white; }
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 0.85rem; color: #aaaaaa; }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def create_card(title, value, suffix=""):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}{suffix}</div>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('dataset/deliveries.csv')
    
    # Phase Classification
    def get_phase(over):
        if over < 6: return "Powerplay"
        elif over < 16: return "Middle"
        else: return "Death"
    df['phase'] = df['over'].apply(get_phase)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Data file not found. Please upload 'deliveries.csv'.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("🏏 IPL PRO ANALYTICS")
analysis_mode = st.sidebar.radio(
    "Select Mode",
    ["Batsman Profiling", "Bowler Arsenal", "Head-to-Head Clash"]
)

# ---------------------------------------------------------
# 4. BATSMAN PROFILING
# ---------------------------------------------------------
if analysis_mode == "Batsman Profiling":
    st.title("🔥 Batsman Profiling")
    
    # 1. Player Selection
    top_batters = df.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).index
    selected_batter = st.selectbox("Search Player", top_batters)
    
    batter_df = df[df['batter'] == selected_batter]
    
    # 2. Key Metrics Row
    total_runs = batter_df['batsman_runs'].sum()
    balls_faced_legal = batter_df[batter_df['extras_type'] != 'wides']
    balls_faced = len(balls_faced_legal)
    matches = batter_df['match_id'].nunique()
    sr = (total_runs / balls_faced * 100) if balls_faced > 0 else 0
    avg = (total_runs / batter_df[batter_df['is_wicket']==1].shape[0]) if batter_df[batter_df['is_wicket']==1].shape[0] > 0 else total_runs
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: create_card("Matches", matches)
    with c2: create_card("Runs", total_runs)
    with c3: create_card("Strike Rate", f"{sr:.1f}")
    with c4: create_card("Average", f"{avg:.1f}")
    with c5: create_card("Boundaries", len(batter_df[batter_df['batsman_runs'].isin([4,6])]))


    total_runs = batter_df['batsman_runs'].sum()
    
    # Filter for legal balls (exclude wides) for accurate ball counts
    legal_balls_df = batter_df[batter_df['extras_type'] != 'wides']
    balls_faced = len(legal_balls_df)
    
    # 1. Overall Strike Rate
    sr = (total_runs / balls_faced * 100) if balls_faced > 0 else 0
    
    # 2. Dot Ball %
    # A dot ball is a legal delivery with 0 runs off the bat
    dot_balls = len(legal_balls_df[legal_balls_df['batsman_runs'] == 0])
    dot_pct = (dot_balls / balls_faced * 100) if balls_faced > 0 else 0
    
    # 3. Boundary %
    # Percentage of balls hit for 4 or 6
    boundaries = len(legal_balls_df[legal_balls_df['batsman_runs'].isin([4, 6])])
    boundary_pct = (boundaries / balls_faced * 100) if balls_faced > 0 else 0
    
    # 4. Powerplay Strike Rate (Overs 0-5)
    pp_df = legal_balls_df[legal_balls_df['over'] < 6]
    pp_runs = pp_df['batsman_runs'].sum()
    pp_balls = len(pp_df)
    pp_sr = (pp_runs / pp_balls * 100) if pp_balls > 0 else 0
    
    # 5. Death Overs Strike Rate (Overs 16-19)
    death_df = legal_balls_df[legal_balls_df['over'] >= 16]
    death_runs = death_df['batsman_runs'].sum()
    death_balls = len(death_df)
    death_sr = (death_runs / death_balls * 100) if death_balls > 0 else 0
    
    # --- Display Metrics ---
    # Using 5 columns for the requested metrics
    c1, c2, c3, c4 = st.columns(4)
    
    with c1: create_card("Dot Ball %", f"{dot_pct:.1f}%")
    with c2: create_card("Boundary %", f"{boundary_pct:.1f}%")
    with c3: create_card("Powerplay SR", f"{pp_sr:.1f}")
    with c4: create_card("Death SR", f"{death_sr:.1f}")

    st.markdown("---")
    
    # 3. Deep Dive Tabs
    tab1, tab2, tab3,tab4  = st.tabs(["📊 Phase Analytics", "⚔️ Matchups & Teams", "📈 Pacing Strategy","🔮 Predictive Insights"])
    
    # --- TAB 1: PHASE ANALYTICS ---
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Boundary Distribution by Phase")
            # 4s and 6s by Phase
            boundaries = batter_df[batter_df['batsman_runs'].isin([4, 6])]
            boundary_stats = boundaries.groupby(['phase', 'batsman_runs']).size().reset_index(name='Count')
            boundary_stats['Type'] = boundary_stats['batsman_runs'].map({4: 'Fours', 6: 'Sixes'})
            
            # Ensure phase order
            phase_order = ['Powerplay', 'Middle', 'Death']
            
            fig_b = px.bar(
                boundary_stats, x='phase', y='Count', color='Type',
                barmode='group',
                category_orders={'phase': phase_order},
                color_discrete_map={'Fours': '#3498db', 'Sixes': '#e74c3c'},
                title="4s & 6s Across Phases"
            )
            fig_b.update_layout(template="plotly_dark")
            st.plotly_chart(fig_b, use_container_width=True)
            
        with col2:
            st.subheader("Dot Ball % by Phase")
            # Calculate Dot % per phase
            phase_dots = batter_df.groupby('phase').apply(lambda x: (x['total_runs'] == 0).sum()).reset_index(name='dots')
            phase_balls = batter_df.groupby('phase').size().reset_index(name='balls')
            dot_stats = pd.merge(phase_dots, phase_balls, on='phase')
            dot_stats['Dot_Percentage'] = (dot_stats['dots'] / dot_stats['balls'] * 100)
            
            fig_dot = px.bar(
                dot_stats, x='phase', y='Dot_Percentage',
                text='Dot_Percentage',
                category_orders={'phase': phase_order},
                color='Dot_Percentage',
                color_continuous_scale='Greys',
                title="Dot Ball Percentage per Phase"
            )
            fig_dot.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_dot.update_layout(template="plotly_dark", yaxis_title="% Dot Balls")
            st.plotly_chart(fig_dot, use_container_width=True)


        col3,col4 = st.columns(2)
        with col3:
            st.subheader("⚡ Phase Dominance")
            # Radar Chart for SR and Avg per phase
            phase_stats = batter_df.groupby('phase').agg({'batsman_runs': 'sum', 'ball': 'count'}).reset_index()
            phase_stats['legal_balls'] = batter_df[batter_df['extras_type'] != 'wides'].groupby('phase').size().values
            phase_stats['SR'] = (phase_stats['batsman_runs'] / phase_stats['legal_balls'] * 100).fillna(0)
            
            # Normalize SR for Radar chart (just for visual shape)
            categories = ['Powerplay', 'Middle', 'Death']
            # Ensure all phases exist
            radar_data = phase_stats.set_index('phase').reindex(categories).fillna(0).reset_index()
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_data['SR'],
                theta=radar_data['phase'],
                fill='toself',
                name='Strike Rate',
                line_color='#00CC96'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 250])),
                template="plotly_dark",
                title="Strike Rate by Phase (Radar)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col4:
            st.subheader("🎯 Scoring Shots")
            # Donut Chart for Scoring
            run_counts = batter_df['batsman_runs'].value_counts().reset_index()
            run_counts.columns = ['Runs', 'Count']
            run_counts['Label'] = run_counts['Runs'].map({0:'Dots', 1:'Singles', 2:'Doubles', 3:'Threes', 4:'Fours', 6:'Sixes', 5:'Fives'})
            
            fig_donut = px.pie(
                run_counts, values='Count', names='Label', hole=0.6,
                color='Label',
                color_discrete_map={'Dots':'#555', 'Singles':'#1f77b4', 'Doubles':'#2ca02c', 'Fours':'#ff7f0e', 'Sixes':'#d62728'},
                title="Run Distribution"
            )
            fig_donut.update_layout(template="plotly_dark", showlegend=True)
            st.plotly_chart(fig_donut, use_container_width=True)

        # --- Trend Analysis ---
        st.subheader("📈 Performance Timeline")
        # Group by Match ID to show consistency
        match_runs = batter_df.groupby('match_id')['batsman_runs'].sum().reset_index()
        fig_trend = px.area(
            match_runs, x=match_runs.index, y='batsman_runs',
            title="Runs Scored per Match (Chronological)",
            labels={'index': 'Match Sequence', 'batsman_runs': 'Runs'},
            template="plotly_dark"
        )
        fig_trend.update_traces(line_color='#636EFA', fillcolor='rgba(99, 110, 250, 0.3)')
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- TAB 2: MATCHUPS & TEAMS ---
    with tab2:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 🐰 Favorite Bowlers (Most Runs)")
            # Group by bowler -> sum runs
            fav_bowlers = batter_df.groupby('bowler')['batsman_runs'].sum().sort_values(ascending=False).head(3).reset_index()
            fig_fav = px.bar(
                fav_bowlers, x='batsman_runs', y='bowler', orientation='h',
                text='batsman_runs',
                title="Most Runs Against",
                color='batsman_runs', color_continuous_scale='Greens'
            )
            fig_fav.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
            st.plotly_chart(fig_fav, use_container_width=True)

        with c2:
            st.markdown("#### 💀 Kryptonite (Most Wickets)")
            # Filter for dismissals where this batter was out
            dismissals = df[(df['batter'] == selected_batter) & (df['is_wicket'] == 1)]
            # Exclude run outs/retired hurt usually as they aren't strictly bowler credit, but user asked for "weakness"
            # Let's stick to bowler credited wickets for strict cricket logic
            valid_modes = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
            dismissals = dismissals[dismissals['dismissal_kind'].isin(valid_modes)]
            
            weak_bowlers = dismissals['bowler'].value_counts().head(3).reset_index()
            weak_bowlers.columns = ['bowler', 'wickets']
            
            fig_weak = px.bar(
                weak_bowlers, x='wickets', y='bowler', orientation='h',
                text='wickets',
                title="Most Dismissals By",
                color='wickets', color_continuous_scale='Reds'
            )
            fig_weak.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
            st.plotly_chart(fig_weak, use_container_width=True)

        #st.subheader("📈 Performance Timeline")
        st.subheader("🏟️ Favorite Teams")
        fav_teams = batter_df.groupby('bowling_team')['batsman_runs'].sum().sort_values(ascending=False).head(3).reset_index()
        fig_team = px.bar(
            fav_teams, x='bowling_team', y='batsman_runs',
            text='batsman_runs',
            title="Most Runs vs Team",
            color='batsman_runs', color_continuous_scale='Bluered'
        )
        fig_team.update_layout(template="plotly_dark", xaxis_title=None)
        st.plotly_chart(fig_team, use_container_width=True)

    # --- TAB 3: PACING STRATEGY ---
    with tab3:
        st.subheader("📈 Innings Progression Analysis")
        st.markdown("*How does the batsman change gears every 10 balls?*")
        
        # Cumulative/Interval SR Logic
        # 1. Rank balls faced within each match for the batter
        # We need to filter legal balls ideally for ball count, but for simplicity let's use all balls faced by him
        pacing_df = batter_df.copy()
        pacing_df['ball_num'] = pacing_df.groupby('match_id').cumcount() + 1
        
        # 2. Bin into 10-ball intervals
        def get_bin(n): return f"{((n-1)//10)*10+1}-{((n-1)//10)*10+10}"
        pacing_df['ball_bucket'] = pacing_df['ball_num'].apply(get_bin)
        pacing_df['bucket_sort'] = ((pacing_df['ball_num']-1)//10)*10 # helper for sorting
        
        # 3. Aggregates
        pacing_stats = pacing_df.groupby(['bucket_sort', 'ball_bucket']).agg({
            'batsman_runs': 'sum',
            'ball_num': 'count'
        }).reset_index()
        
        pacing_stats['Strike_Rate'] = (pacing_stats['batsman_runs'] / pacing_stats['ball_num'] * 100)
        
        # Filter out buckets with very low sample size (e.g., late innings that rarely happen)
        # Optional: pacing_stats = pacing_stats[pacing_stats['ball_num'] > 20] 

        fig_pace = px.line(
            pacing_stats, x='ball_bucket', y='Strike_Rate',
            markers=True,
            title="Strike Rate by Balls Faced Interval (1-10, 11-20, etc.)",
            labels={'ball_bucket': 'Ball Interval', 'Strike_Rate': 'Strike Rate'},
            line_shape='spline'
        )
        fig_pace.update_traces(line_color='#00CC96', line_width=4)
        fig_pace.add_bar(
            x=pacing_stats['ball_bucket'], y=pacing_stats['Strike_Rate'], 
            opacity=0.2, name='Magnitude'
        )
        fig_pace.update_layout(template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig_pace, use_container_width=True)

        st.subheader("🚀 Acceleration & Risk Profile")
        # st.markdown("---")
        
        # --- PRE-PROCESSING: INTERVAL DATA ---
        # 1. Sort and rank balls faced to create 10-ball intervals
        # We use legal balls only for accurate 'balls faced' count
        timeline_df = batter_df[batter_df['extras_type'] != 'wides'].sort_values(['match_id', 'over', 'ball']).copy()
        timeline_df['ball_cum'] = timeline_df.groupby('match_id').cumcount() + 1
        
        # 2. Binning (1-10, 11-20, etc.)
        timeline_df['ball_interval'] = ((timeline_df['ball_cum'] - 1) // 10) * 10 + 10
        
        # 3. Aggregate Metrics per Interval
        # We take the average behavior across all matches for these intervals
        interval_stats = timeline_df.groupby('ball_interval').agg({
            'batsman_runs': 'sum',
            'is_wicket': 'sum',
            'ball_cum': 'count' # This acts as denominator (balls in bucket)
        }).reset_index()
        
        # Calculate Custom Metrics
        # A. Interval Strike Rate (The "Speed" at that moment)
        interval_stats['Interval_SR'] = (interval_stats['batsman_runs'] / interval_stats['ball_cum'] * 100)
        
        # B. Momentum Change (Acceleration)
        # Change in SR compared to previous interval
        interval_stats['Momentum_Change'] = interval_stats['Interval_SR'].diff().fillna(0)
        
        # C. Aggression Index (Boundaries per ball in interval)
        # We need to count boundaries in each interval first
        boundaries_per_interval = timeline_df[timeline_df['batsman_runs'].isin([4, 6])].groupby('ball_interval').size()
        interval_stats = interval_stats.set_index('ball_interval')
        interval_stats['boundaries'] = boundaries_per_interval
        interval_stats = interval_stats.fillna(0).reset_index()
        
        interval_stats['Aggression_Index'] = interval_stats['boundaries'] / interval_stats['ball_cum']

        # --- VISUAL 1: ACCELERATION CURVE (Momentum) ---
        st.subheader("Acceleration Curve (Momentum Change)")
        st.caption("Shows how the batsman's Strike Rate changes from one 10-ball block to the next. Positive bars = Accelerating.")
        
        # We use a Color bar chart to show positive (Green) vs negative (Red) momentum shift
        interval_stats['Color'] = interval_stats['Momentum_Change'].apply(lambda x: '#00CC96' if x >= 0 else '#EF553B')
        
        fig_accel = go.Figure()
        
        # Add the Bars (Delta)
        fig_accel.add_trace(go.Bar(
            x=interval_stats['ball_interval'], 
            y=interval_stats['Momentum_Change'],
            marker_color=interval_stats['Color'],
            name='SR Change'
        ))
        
        # Overlay the Actual SR Curve to provide context
        fig_accel.add_trace(go.Scatter(
            x=interval_stats['ball_interval'],
            y=interval_stats['Interval_SR'],
            mode='lines+markers',
            name='Actual Strike Rate',
            line=dict(color='white', width=2, dash='dot'),
            yaxis='y2'
        ))
        
        fig_accel.update_layout(
            template="plotly_dark",
            xaxis_title="Balls Faced Interval (e.g., 10 = balls 1-10)",
            yaxis_title="Change in Strike Rate",
            yaxis2=dict(title="Actual Strike Rate", overlaying='y', side='right', showgrid=False),
            title="Momentum Shift per 10 Balls",
            hovermode="x unified"
        )
        st.plotly_chart(fig_accel, use_container_width=True)

        # --- VISUAL 2 & 3: SPLIT LAYOUT ---
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Wicket Vulnerability")
            st.caption("In which over did the batsman get out?")
            # Filter for actual dismissals of the batter
            dismissals = df[(df['batter'] == selected_batter) & (df['is_wicket'] == 1)]
            dismissal_counts = dismissals['over'].value_counts().reset_index()
            dismissal_counts.columns = ['over', 'count']
            dismissal_counts = dismissal_counts.sort_values('over')
            
            # Add 1 to over for display (1-20 instead of 0-19)
            dismissal_counts['display_over'] = dismissal_counts['over'] + 1
            
            fig_wickets = px.bar(
                dismissal_counts, 
                x='display_over', 
                y='count',
                title="Dismissals per Over Number",
                labels={'display_over': 'Over Number (1-20)', 'count': 'Times Dismissed'},
                color='count',
                color_continuous_scale='Reds'
            )
            fig_wickets.update_layout(template="plotly_dark", xaxis=dict(tickmode='linear', dtick=1))
            st.plotly_chart(fig_wickets, use_container_width=True)
            
        with c2:
            st.subheader("Aggression Index")
            st.caption("Aggression = (4s + 6s) / Balls Faced. Higher area means higher boundary frequency.")
            
            fig_agg = px.area(
                interval_stats, 
                x='ball_interval', 
                y='Aggression_Index',
                title="Aggression Index (Boundaries per Ball)",
                labels={'ball_interval': 'Balls Faced Interval', 'Aggression_Index': 'Boundary Probability'},
                line_shape='spline'
            )
            # Fill style
            fig_agg.update_traces(line_color='#AB63FA', fillcolor='rgba(171, 99, 250, 0.4)')
            fig_agg.update_layout(template="plotly_dark", yaxis_tickformat=".0%")
            st.plotly_chart(fig_agg, use_container_width=True)


    with tab4:
        st.subheader("🔮 Predictive Insights")
    
        # 1. Filter for Legal Balls (Basis for probability)
        legal_balls_df = batter_df[batter_df['extras_type'] != 'wides']
        
        # --- METRIC 1: FRUSTRATION INDEX ---
        # Logic: Average number of consecutive dot balls immediately preceding a boundary (4 or 6)
        # This indicates how much pressure a batsman absorbs before releasing it.
        
        frustration_counts = []
        current_dots = 0
        
        # Iterate through balls sorted by time
        # Note: Sorting is crucial for sequence logic
        sorted_df = legal_balls_df.sort_values(['match_id', 'over', 'ball'])
        
        for runs in sorted_df['batsman_runs']:
            if runs == 0:
                current_dots += 1
            elif runs in [4, 6]:
                frustration_counts.append(current_dots)
                current_dots = 0
            else:
                # Running 1, 2, or 3 releases pressure but isn't a "release shot"
                current_dots = 0
                
        frustration_index = sum(frustration_counts) / len(frustration_counts) if frustration_counts else 0

        # --- METRIC 2 & 3: PROBABILITY METRICS ---
        # Definition: Probability of event occurring at least once in a random 10-ball chunk
        # Formula: 1 - (1 - p)^10
        
        total_balls = len(legal_balls_df)
        
        # Boundary Probability
        boundary_count = len(legal_balls_df[legal_balls_df['batsman_runs'].isin([4, 6])])
        p_boundary_per_ball = boundary_count / total_balls if total_balls > 0 else 0
        prob_boundary_10 = (1 - (1 - p_boundary_per_ball)**10) * 100
        
        # Wicket Probability
        # Filter for dismissals of this specific batter
        # (Exclude run-outs at non-striker end, ensure player_dismissed is the batter)
        valid_wickets = batter_df[
            (batter_df['is_wicket'] == 1) & 
            (batter_df['player_dismissed'] == selected_batter)
        ]
        wicket_count = len(valid_wickets)
        p_wicket_per_ball = wicket_count / total_balls if total_balls > 0 else 0
        prob_wicket_10 = (1 - (1 - p_wicket_per_ball)**10) * 100

        # --- DISPLAY METRICS ---
        def create_gradient_card(title, value, desc, color_hex, icon):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
                border-left: 5px solid {color_hex};
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="color: #aaa; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{title}</span>
                    <span style="font-size: 1.5rem;">{icon}</span>
                </div>
                <div style="font-size: 2.2rem; font-weight: 700; color: white; margin-bottom: 8px;">
                    {value}
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); font-style: italic;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. Render Cards
        c1, c2, c3 = st.columns(3)
        
        with c1:
            create_gradient_card(
                title="Frustration Index", 
                value=f"{frustration_index:.2f}", 
                desc="Avg dots absorbed before hitting a boundary. High = Patient Power.",
                color_hex="#FFA500", # Orange
                icon="😤"
            )
            
        with c2:
            create_gradient_card(
                title="Boundary Prob.", 
                value=f"{prob_boundary_10:.1f}%", 
                desc="Chance of hitting a 4 or 6 in the next 10 balls.",
                color_hex="#00CC96", # Green
                icon="🔥"
            )
            
        with c3:
            create_gradient_card(
                title="Wicket Hazard", 
                value=f"{prob_wicket_10:.1f}%", 
                desc="Risk of getting out in the next 10 balls.",
                color_hex="#EF553B", # Red
                icon="⚠️"
            )

# ---------------------------------------------------------
# 5. BOWLER ARSENAL (KEPT AS IS)
# ---------------------------------------------------------
elif analysis_mode == "Bowler Arsenal":
    st.title("🎯 Bowler Arsenal")
    
    # 1. Player Selection
    # Sort by wickets for better default list
    bowler_wickets = df[df['is_wicket'] == 1]['bowler'].value_counts()
    selected_bowler = st.selectbox("Search Bowler", bowler_wickets.index)
    
    bowler_df = df[df['bowler'] == selected_bowler]
    
    # 2. Key Metrics Row
    # --- Logic for Bowler Runs & Wickets ---
    # Runs Conceded: Total runs - (legbyes + byes + penalty)
    mask_extras = bowler_df['extras_type'].isin(['legbyes', 'byes', 'penalty'])
    bowler_run_data = bowler_df['total_runs'].copy()
    bowler_run_data[mask_extras] -= bowler_df.loc[mask_extras, 'extra_runs']
    runs_conceded = bowler_run_data.sum()
    
    # Legal Balls (for Economy & SR)
    legal_balls_df = bowler_df[~bowler_df['extras_type'].isin(['wides', 'noballs'])]
    legal_balls_count = len(legal_balls_df)
    overs_bowled = legal_balls_count / 6
    
    # Wickets (exclude run-outs which aren't bowler's credit)
    valid_dismissals = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wicket_df = bowler_df[(bowler_df['is_wicket'] == 1) & (bowler_df['dismissal_kind'].isin(valid_dismissals))]
    total_wickets = len(wicket_df)
    
    # Metrics
    matches = bowler_df['match_id'].nunique()
    economy = (runs_conceded / overs_bowled) if overs_bowled > 0 else 0
    bowling_avg = (runs_conceded / total_wickets) if total_wickets > 0 else 0
    bowling_sr = (legal_balls_count / total_wickets) if total_wickets > 0 else 0
    
    # Dot Ball %
    # Dot ball for bowler: No runs off bat and no extras (except maybe legbyes, but let's keep simple: total_runs=0)
    # Strictly speaking, a legbye is a dot for the bowler. 
    # Let's count balls where runs_conceded == 0
    dot_balls = len(bowler_df[bowler_run_data == 0])
    dot_pct = (dot_balls / len(bowler_df) * 100) if len(bowler_df) > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: create_card("Wickets", total_wickets, " 🎯")
    with c2: create_card("Economy", f"{economy:.2f}")
    with c3: create_card("Average", f"{bowling_avg:.1f}")
    with c4: create_card("Strike Rate", f"{bowling_sr:.1f}")
    with c5: create_card("Dot Ball %", f"{dot_pct:.1f}%")
    
    st.markdown("---")

    # 3. Deep Dive Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Phase Analytics", "💀 Wicket Analysis", "📉 Spell Strategy", "🔮 Predictive Insights"])

    # --- TAB 1: PHASE ANALYTICS ---
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Economy Rate by Phase")
            # Need to recalculate runs/balls per phase
            phase_grp = bowler_df.groupby('phase')
            phases = []
            
            for phase in ['Powerplay', 'Middle', 'Death']:
                if phase in phase_grp.groups:
                    p_data = phase_grp.get_group(phase)
                    
                    # Recalc runs
                    p_mask = p_data['extras_type'].isin(['legbyes', 'byes', 'penalty'])
                    p_runs = p_data['total_runs'].copy()
                    p_runs[p_mask] -= p_data.loc[p_mask, 'extra_runs']
                    total_p_runs = p_runs.sum()
                    
                    # Recalc legal balls
                    p_legal = len(p_data[~p_data['extras_type'].isin(['wides', 'noballs'])])
                    p_overs = p_legal / 6
                    
                    eco = (total_p_runs / p_overs) if p_overs > 0 else 0
                    phases.append({'Phase': phase, 'Economy': eco, 'Runs': total_p_runs})
            
            phase_df = pd.DataFrame(phases)
            if not phase_df.empty:
                fig_eco = px.bar(
                    phase_df, x='Phase', y='Economy',
                    text='Economy', color='Economy',
                    color_continuous_scale='RdYlGn_r', # Red is high (bad for bowler)
                    title="Economy Control"
                )
                fig_eco.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig_eco.update_layout(template="plotly_dark")
                st.plotly_chart(fig_eco, use_container_width=True)
                
        with col2:
            st.subheader("Wickets by Phase")
            # Count wickets per phase
            w_phase = wicket_df['phase'].value_counts().reset_index()
            w_phase.columns = ['Phase', 'Wickets']
            
            fig_w_phase = px.pie(
                w_phase, values='Wickets', names='Phase',
                hole=0.6,
                color_discrete_sequence=px.colors.sequential.Plasma,
                title="Wicket Distribution"
            )
            fig_w_phase.update_layout(template="plotly_dark")
            st.plotly_chart(fig_w_phase, use_container_width=True)

        col3,col4 = st.columns(2)
        phase_metrics = bowler_df.groupby('phase').apply(lambda x: pd.Series({
            'balls': len(x),
            'legal_balls': len(x[~x['extras_type'].isin(['wides', 'noballs'])]),
            'dots': len(x[x['total_runs'] == 0]),
            'wickets': len(x[x['is_wicket'] == 1]),
            # Calculate runs excluding byes/legbyes for Economy
            'runs_conceded': x['total_runs'].sum() - x[x['extras_type'].isin(['legbyes', 'byes', 'penalty'])]['extra_runs'].sum() if not x.empty else 0
        })).reset_index()
        
        # Calculate Metrics
        phase_metrics['Economy'] = (phase_metrics['runs_conceded'] / (phase_metrics['legal_balls'] / 6)).fillna(0)
        phase_metrics['Dot_Percentage'] = (phase_metrics['dots'] / phase_metrics['balls'] * 100).fillna(0)
        phase_metrics['Wicket_Prob'] = (phase_metrics['wickets'] / phase_metrics['balls'] * 100).fillna(0)
        
        # Order Phases: Powerplay -> Middle -> Death
        phase_order = ['Powerplay', 'Middle', 'Death']
        phase_metrics['phase'] = pd.Categorical(phase_metrics['phase'], categories=phase_order, ordered=True)
        phase_metrics = phase_metrics.sort_values('phase')

        with col3:
            # --- Economy Radar Chart ---
            st.subheader("Economy Rate Structure")
            
            # Prepare data for Radar
            categories = phase_metrics['phase'].tolist()
            values = phase_metrics['Economy'].tolist()
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Economy',
                line_color='#00CC96',
                opacity=0.7
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, max(values, default=10) + 2])
                ),
                template="plotly_dark",
                title="Economy Radar",
                margin=dict(t=40, b=40)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col4:
            st.subheader("Dot Ball Percentage per Phase")
            
            fig_dot = px.bar(
                phase_metrics, 
                x='phase', 
                y='Dot_Percentage',
                text='Dot_Percentage',
                title="Stifling Power (Dot %)",
                color='Dot_Percentage',
                color_continuous_scale='Blues'
            )
            fig_dot.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_dot.update_layout(template="plotly_dark", yaxis_title="Dot %")
            st.plotly_chart(fig_dot, use_container_width=True)
            
        # --- Wicket Taking Probability (Bar Chart) ---
        st.subheader("Phase Wise Wicket taking Probability")
        
        fig_prob = px.bar(
            phase_metrics,
            x='phase',
            y='Wicket_Prob',
            text='Wicket_Prob',
            title="Wicket Probability by Phase",
            color='Wicket_Prob',
            color_continuous_scale='Reds' # Red indicates Danger/Wickets
        )
        fig_prob.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_prob.update_layout(template="plotly_dark", yaxis_title="Probability %")
        st.plotly_chart(fig_prob, use_container_width=True)

    # --- TAB 2: WICKET ANALYSIS ---
    with tab2:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### 🐰 The Bunnies (Most Dismissed)")
            # Who has this bowler dismissed most?
            bunnies = wicket_df['player_dismissed'].value_counts().head(5).reset_index()
            bunnies.columns = ['Batsman', 'Dismissals']
            
            fig_bunny = px.bar(
                bunnies, y='Batsman', x='Dismissals', orientation='h',
                text='Dismissals',
                color='Dismissals', color_continuous_scale='Oranges',
                title="Batters Dismissed Most Often"
            )
            fig_bunny.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bunny, use_container_width=True)

        with c2:
            st.markdown("#### 🥵 The Smashers (Weakness)")
            #st.caption("Batsmen who have scored the most runs against this bowler.")
            
            # Group by batter to find who scored most runs
            weakness = bowler_df.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(5).reset_index()
            
            fig_weak = px.bar(
                weakness, x='batsman_runs', y='batter', orientation='h',
                text='batsman_runs',
                title="Most Runs Conceded Against",
                color='batsman_runs',
                color_continuous_scale='Reds' # Red indicates high runs conceded (bad for bowler)
            )
            fig_weak.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_weak, use_container_width=True)

        col3,col4 = st.columns(2)  
        with col3:
            st.markdown("#### 🕸️ Dismissal Methods")
            fig_type = px.pie(
                wicket_df, names='dismissal_kind', 
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="How do they get wickets?"
            )
            fig_type.update_layout(template="plotly_dark")
            st.plotly_chart(fig_type, use_container_width=True)

        with col4:
            st.markdown("#### 🦁 Favorite Opponents")
            #st.caption("Teams against whom this bowler takes the most wickets.")
            
            # Count wickets against each batting team
            # We use wicket_df which was already filtered for valid dismissals
            team_wickets = wicket_df['batting_team'].value_counts().head(5).reset_index()
            team_wickets.columns = ['Team', 'Wickets']
            
            fig_team = px.bar(
                team_wickets, x='Wickets', y='Team', orientation='h',
                text='Wickets',
                title="Most Wickets vs Team",
                color='Wickets',
                color_continuous_scale='Greens' # Green indicates high wickets (good for bowler)
            )
            fig_team.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_team, use_container_width=True)

    # --- TAB 3: SPELL STRATEGY ---
    with tab3:
        st.subheader("📉 Effectiveness by Over Number")
        st.caption("Which overs of the match (1-20) is the bowler most dangerous in?")
        
        # Group by Over Number
        # We need sum of wickets and sum of runs per over number across all matches
        over_stats = bowler_df.groupby('over').agg({
            'total_runs': 'sum', # Approx for visualization
            'is_wicket': 'sum',
            'match_id': 'nunique'
        }).reset_index()
        
        # Adjust over index to 1-20
        over_stats['display_over'] = over_stats['over'] + 1
        
        # Calculate strict runs conceded (re-applying logic slightly simplified for speed here)
        # For precise 'Runs per Over' visualization
        # Let's filter just valid dismissals for the wicket count
        real_wickets = bowler_df[bowler_df['dismissal_kind'].isin(valid_dismissals)].groupby('over').size().reindex(over_stats['over'], fill_value=0).values
        over_stats['Wickets'] = real_wickets
        
        fig_spell = go.Figure()
        
        # Bar for Wickets
        fig_spell.add_trace(go.Bar(
            x=over_stats['display_over'], 
            y=over_stats['Wickets'],
            name='Wickets',
            marker_color='#EF553B'
        ))
        
        # Line for Runs (Volume)
        fig_spell.add_trace(go.Scatter(
            x=over_stats['display_over'],
            y=over_stats['total_runs'],
            name='Total Runs Conceded',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#00CC96', width=2)
        ))
        
        fig_spell.update_layout(
            template="plotly_dark",
            title="Wickets & Runs per Over Number (Career)",
            xaxis=dict(title="Over Number (1-20)", tickmode='linear', dtick=1),
            yaxis=dict(title="Total Wickets"),
            yaxis2=dict(title="Total Runs", overlaying='y', side='right', showgrid=False),
            hovermode="x unified",
            legend=dict(x=0, y=1.1, orientation='h')
        )
        st.plotly_chart(fig_spell, use_container_width=True)


        st.subheader("🌊 Momentum & Risk Profile (Spell Progression)")
        st.caption("Analyzing performance evolution from the 1st over of a spell onwards.")

        # --- PRE-PROCESSING: SPELL INTERVAL DATA ---
        # 1. Sort and rank balls bowled within each match
        # We use legal balls to approximate 'overs bowled' correctly
        spell_df = bowler_df[~bowler_df['extras_type'].isin(['wides', 'noballs'])].sort_values(['match_id', 'over', 'ball']).copy()
        spell_df['ball_cum'] = spell_df.groupby('match_id').cumcount() + 1
        
        # 2. Bin into "Overs" (Intervals of 6 balls: 1-6, 7-12, etc.)
        spell_df['over_interval'] = ((spell_df['ball_cum'] - 1) // 6) + 1
        
        # 3. Calculate Runs for these specific balls
        # Aggregate per Interval (Average across career)
        spell_stats = spell_df.groupby('over_interval').agg({
            'total_runs': 'sum', # Includes legbyes/byes, slightly overestimates bowler runs but consistent for trend
            'ball_cum': 'count'
        }).reset_index()
        
        # Calculate Interval Economy
        # Runs / (Balls/6) -> Runs / 1 (since interval is 6 balls) -> Runs
        # But we need to average per match? No, we aggregate all runs in that interval number / total balls.
        # Eco = (Total Runs in Interval X across career) / (Total Overs in Interval X across career)
        spell_stats['Interval_Economy'] = (spell_stats['total_runs'] / spell_stats['ball_cum']) * 6
        
        # 1. Momentum Shift (Delta Economy)
        spell_stats['Eco_Change'] = spell_stats['Interval_Economy'].diff().fillna(0)
        
        # 2. Risk Allowance (Boundaries per Over)
        # Count boundaries in the filtered dataset
        boundaries_per_interval = spell_df[spell_df['batsman_runs'].isin([4, 6])].groupby('over_interval').size()
        spell_stats = spell_stats.set_index('over_interval')
        spell_stats['boundaries'] = boundaries_per_interval
        spell_stats = spell_stats.fillna(0).reset_index()
        
        spell_stats['Risk_Index'] = spell_stats['boundaries'] / (spell_stats['ball_cum'] / 6) # Boundaries per Over
        
        # Limit to first 4-5 overs (typical spell length) to avoid noisy tail data
        spell_stats = spell_stats[spell_stats['over_interval'] <= 4] 

        # --- VISUALS ---
        
        st.subheader("Bowling Momentum Shift")
        st.caption("Change in Economy Rate between consecutive overs of a spell. Green = Tightening up.")
        
        # Logic: Negative Change in Economy is GOOD (Green), Positive is BAD (Red)
        spell_stats['Color'] = spell_stats['Eco_Change'].apply(lambda x: '#00CC96' if x <= 0 else '#EF553B')
        
        fig_mom = go.Figure()
        fig_mom.add_trace(go.Bar(
            x=spell_stats['over_interval'],
            y=spell_stats['Eco_Change'],
            marker_color=spell_stats['Color'],
            name='Economy Delta'
        ))
        
        # Overlay Actual Economy
        fig_mom.add_trace(go.Scatter(
            x=spell_stats['over_interval'],
            y=spell_stats['Interval_Economy'],
            mode='lines+markers',
            name='Actual Economy',
            line=dict(color='white', width=2, dash='dot'),
            yaxis='y2'
        ))
        
        fig_mom.update_layout(
            template="plotly_dark",
            xaxis_title="Over Number in Spell (1st, 2nd...)",
            yaxis_title="Change in Economy",
            yaxis2=dict(title="Actual Economy", overlaying='y', side='right', showgrid=False),
            title="Economy Delta per Over",
            hovermode="x unified"
        )
        st.plotly_chart(fig_mom, use_container_width=True)
        
    
        st.subheader("Risk Allowance Index")
        st.caption("Average number of Boundaries (4s + 6s) conceded per over in the spell.")
        
        fig_risk = px.area(
            spell_stats,
            x='over_interval',
            y='Risk_Index',
            title="Boundary Probability per Over",
            labels={'over_interval': 'Over Number in Spell', 'Risk_Index': 'Boundaries per Over'},
            line_shape='spline'
        )
        fig_risk.update_traces(line_color='#FF4136', fillcolor='rgba(255, 65, 54, 0.3)')
        fig_risk.update_layout(template="plotly_dark")
        st.plotly_chart(fig_risk, use_container_width=True)

    # --- TAB 4: PREDICTIVE INSIGHTS ---
    with tab4:
        st.subheader("🔮 Predictive Insights")
        
        # 1. Setup Index: Dots before Wicket
        # Logic: Average number of dot balls in the 6 balls leading up to a wicket
        setup_dots = []
        
        # Sort chronologically
        sorted_bowler = bowler_df.sort_values(['match_id', 'over', 'ball'])
        
        # We identify wicket indices
        wicket_indices = sorted_bowler[sorted_bowler['is_wicket'] == 1].index
        
        # This is computationally heavy to iterate all, so we iterate wickets
        # We need a way to access 'prev 6 balls' efficiently. 
        # Convert to list/array for speed
        runs_array = bowler_run_data.loc[sorted_bowler.index].values
        is_wicket_array = sorted_bowler['is_wicket'].values
        
        for i in range(len(is_wicket_array)):
            if is_wicket_array[i] == 1:
                # Look back up to 6 balls (ensure not crossing match boundary? Ignored for simplicity in this window)
                start_idx = max(0, i-6)
                window = runs_array[start_idx:i]
                # Count zeros
                dots = np.sum(window == 0)
                setup_dots.append(dots)
                
        setup_index = np.mean(setup_dots) if setup_dots else 0
        
        # 2. Probability Metrics
        total_balls_bowled = len(bowler_df)
        
        # Wicket Probability (Lethality)
        p_wicket_ball = total_wickets / total_balls_bowled if total_balls_bowled > 0 else 0
        prob_wicket_10 = (1 - (1 - p_wicket_ball)**10) * 100
        
        # Boundary Probability (Leakage)
        boundaries_conceded = len(bowler_df[bowler_df['batsman_runs'].isin([4, 6])])
        p_boundary_ball = boundaries_conceded / total_balls_bowled if total_balls_bowled > 0 else 0
        prob_boundary_10 = (1 - (1 - p_boundary_ball)**10) * 100

        # --- Helper for Gradient Cards (Redefined here for scope safety) ---
        def create_gradient_card(title, value, desc, color_hex, icon):
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
                border-left: 5px solid {color_hex};
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="color: #aaa; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{title}</span>
                    <span style="font-size: 1.5rem;">{icon}</span>
                </div>
                <div style="font-size: 2.2rem; font-weight: 700; color: white; margin-bottom: 8px;">
                    {value}
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6); font-style: italic;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Render
        c1, c2, c3 = st.columns(3)
        
        with c1:
            create_gradient_card(
                title="Setup Index",
                value=f"{setup_index:.1f}",
                desc="Avg dot balls bowled in the 6 balls prior to taking a wicket.",
                color_hex="#636EFA", # Blue
                icon="♟️"
            )
        
        with c2:
            create_gradient_card(
                title="Wicket Prob.",
                value=f"{prob_wicket_10:.1f}%",
                desc="Chance of taking a wicket in the next 10 balls.",
                color_hex="#00CC96", # Green
                icon="🎯"
            )
            
        with c3:
            create_gradient_card(
                title="Boundary Risk",
                value=f"{prob_boundary_10:.1f}%",
                desc="Chance of conceding a boundary in the next 10 balls.",
                color_hex="#EF553B", # Red
                icon="💣"
            )
# ---------------------------------------------------------
# 6. HEAD TO HEAD
# ---------------------------------------------------------
elif analysis_mode == "Head-to-Head Clash":
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>⚔️ The Ultimate Face-Off ⚔️</h1>", unsafe_allow_html=True)

    # Selectors with a "VS" layout
    c1, c2, c3 = st.columns([5, 2, 5])
    with c1:
        st.markdown("### 🏏 The Batter")
        batter = st.selectbox("Choose Batter", sorted(df['batter'].unique()), label_visibility="collapsed")
    with c2:
        st.markdown("<h2 style='text-align: center; margin-top: 20px;'>VS</h2>", unsafe_allow_html=True)
    with c3:
        st.markdown("### 🎯 The Bowler")
        # Smart filter: only show bowlers who have bowled to this batter
        opponents = df[df['batter'] == batter]['bowler'].unique()
        bowler = st.selectbox("Choose Bowler", sorted(opponents), label_visibility="collapsed")

    # Filter Data
    h2h = df[(df['batter'] == batter) & (df['bowler'] == bowler)]

    # --- ANALYSIS SECTION ---
    if not h2h.empty:
        # 1. Advanced Metrics Calculation
        total_runs = h2h['batsman_runs'].sum()
        balls_faced = len(h2h[h2h['extras_type'] != 'wides'])
        dismissals = len(h2h[h2h['is_wicket'] == 1])
        
        # Avoid division by zero
        strike_rate = (total_runs / balls_faced * 100) if balls_faced > 0 else 0
        dot_balls = len(h2h[h2h['batsman_runs'] == 0])
        dot_percentage = (dot_balls / balls_faced * 100) if balls_faced > 0 else 0
        
        # 2. The Verdict Logic (Just for fun/context)
        if dismissals >= 3:
            verdict = f"🐰 {batter} is {bowler}'s bunny! (Dismissed {dismissals} times)"
            verdict_color = "red"
        elif strike_rate > 170:
            verdict = f"🔥 {batter} smashes {bowler} everywhere! (SR: {strike_rate:.1f})"
            verdict_color = "green"
        elif strike_rate < 100:
            verdict = f"🔒 {bowler} keeps {batter} quiet. (SR: {strike_rate:.1f})"
            verdict_color = "orange"
        else:
            verdict = "⚖️ An evenly matched contest."
            verdict_color = "blue"

        st.markdown(f"<div style='background-color: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; text-align: center; color: {verdict_color}; margin-bottom: 20px;'><h3>{verdict}</h3></div>", unsafe_allow_html=True)

        # 3. High-Impact Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Runs", total_runs, delta=None)
        m2.metric("Balls Faced", balls_faced, delta=None)
        m3.metric("Strike Rate", f"{strike_rate:.1f}", delta_color="normal")
        m4.metric("Dismissals", dismissals, delta_color="inverse")

        st.markdown("---")

        # 4. Visualization Layout
        col_viz1, col_viz2 = st.columns([2, 1])

        with col_viz1:
            st.subheader("📊 The Timeline (Runs vs Momentum)")
            
            # 1. Prepare Data
            h2h = h2h.reset_index(drop=True)
            h2h['ball_seq'] = h2h.index + 1
            h2h['cumulative_runs'] = h2h['batsman_runs'].cumsum() # The Line Graph Data
            
            # Color logic for bars
            def get_color(row):
                if row['is_wicket'] == 1: return '#FF4B4B' # Red for Wicket bar
                if row['batsman_runs'] == 6: return '#800080'
                if row['batsman_runs'] == 4: return '#0000FF'
                if row['batsman_runs'] == 0: return '#2C2C2C' # Dark Grey for dots
                return '#00CC96'

            h2h['color'] = h2h.apply(get_color, axis=1)
            
            # 2. Create Dual-Axis Plot
            fig_timeline = make_subplots(specs=[[{"secondary_y": True}]])

            # LAYER 1: The Bars (Runs per Ball) - Primary Y Axis
            fig_timeline.add_trace(
                go.Bar(
                    x=h2h['ball_seq'],
                    y=h2h['batsman_runs'],
                    marker_color=h2h['color'],
                    name='Runs per Ball',
                    text=h2h['batsman_runs'],
                    textposition='auto',
                    hoverinfo='text+x+y',
                    opacity=0.7 # Slight transparency to let the line pop
                ),
                secondary_y=False
            )

            # LAYER 2: The Line (Cumulative Score) - Secondary Y Axis
            fig_timeline.add_trace(
                go.Scatter(
                    x=h2h['ball_seq'],
                    y=h2h['cumulative_runs'],
                    mode='lines+markers',
                    name='Total Score',
                    line=dict(color='#FFA500', width=3), # Bright Orange Line
                    marker=dict(size=6, color='#FFA500')
                ),
                secondary_y=True
            )

            # LAYER 3: The Wickets (Distinct Markers)
            wickets = h2h[h2h['is_wicket'] == 1]
            if not wickets.empty:
                fig_timeline.add_trace(
                    go.Scatter(
                        x=wickets['ball_seq'],
                        y=wickets['cumulative_runs'], # Place marker on the line
                        mode='markers',
                        name='Wicket',
                        marker=dict(
                            symbol='circle', 
                            size=18, 
                            color='red', 
                            line=dict(width=2, color='white') # Red circle with white border
                        ),
                        hoverinfo='text',
                        text=['WICKET!'] * len(wickets)
                    ),
                    secondary_y=True
                )

            # 3. Layout Polish
            fig_timeline.update_layout(
                title=None,
                template="plotly_dark",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400,
                hovermode="x unified" # Shows both bar and line data on hover
            )

            # Axis Titles
            fig_timeline.update_yaxes(title_text="Runs per Ball", secondary_y=False, showgrid=False)
            fig_timeline.update_yaxes(title_text="Cumulative Score", secondary_y=True, showgrid=True, gridcolor='rgba(128,128,128,0.2)')
            fig_timeline.update_xaxes(title_text="Ball Sequence")

            st.plotly_chart(fig_timeline, use_container_width=True)

        with col_viz2:
            st.subheader("🎯 Scoring Dist.")
            
            # Data for Pie Chart
            run_counts = h2h['batsman_runs'].value_counts().reset_index()
            run_counts.columns = ['runs', 'count']
            
            # Custom mapping for legend
            run_counts['category'] = run_counts['runs'].apply(lambda x: f"{x}s" if x != 1 else "1s")
            
            fig_donut = px.pie(
                run_counts, 
                values='count', 
                names='category', 
                hole=0.5,
                color='runs',
                color_discrete_map={0: '#D3D3D3', 1: '#00CC96', 2: '#00CC96', 3: '#00CC96', 4: '#0000FF', 6: '#800080'}
            )
            fig_donut.update_layout(
                title=f"Dot Ball %: {dot_percentage:.1f}%",
                template="plotly_dark",
                showlegend=False
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_donut, use_container_width=True)

    else:
        st.info("No historical face-offs found between these two giants.")



    st.markdown("---")
    st.markdown("## 🧠 Deep Dive Analytics")

    # --- SECTION 1: OUTCOME PROBABILITY HEATMAP ---
    # We calculate the % chance of every specific outcome for this matchup
    st.subheader("Outcome Probability Distribution")
    
    outcomes = [0, 1, 2, 3, 4, 6]
    prob_data = []
    
    # Calculate percentages
    total_balls = len(h2h)
    for r in outcomes:
        count = len(h2h[h2h['batsman_runs'] == r])
        prob = (count / total_balls) * 100 if total_balls > 0 else 0
        prob_data.append({'Outcome': str(r), 'Probability': prob})
        
    # Add Wicket Probability
    w_count = len(h2h[h2h['is_wicket'] == 1])
    w_prob = (w_count / total_balls) * 100 if total_balls > 0 else 0
    prob_data.append({'Outcome': 'W', 'Probability': w_prob})

    prob_df = pd.DataFrame(prob_data)
    
    # Create a single-row heatmap
    fig_heat = go.Figure(data=go.Heatmap(
        z=[prob_df['Probability']],
        x=prob_df['Outcome'],
        y=['Probability %'],
        colorscale='Viridis',
        texttemplate="%{z:.1f}%",
        showscale=False
    ))
    fig_heat.update_layout(title="Shot Outcome Probability Grid", height=150, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)


    # --- SECTION 2: CONTEXT SCATTER (Batter vs All Bowlers) ---
    st.subheader(f"{batter}'s Performance vs Different Bowlers")
    st.caption("See how this bowler compares to everyone else this batter has faced.")

    # 1. Get stats for this batter against ALL bowlers
    batter_all = df[df['batter'] == batter]
    stats_list = []

    for b_name in batter_all['bowler'].unique():
        b_df = batter_all[batter_all['bowler'] == b_name]
        runs = b_df['batsman_runs'].sum()
        balls = len(b_df[b_df['extras_type'] != 'wides'])
        wickets = len(b_df[b_df['is_wicket'] == 1])
        
        if balls > 10: # Filter for meaningful sample size
            sr = (runs / balls) * 100
            boundary_balls = len(b_df[b_df['batsman_runs'].isin([4, 6])])
            boundary_pct = (boundary_balls / balls) * 100
            wkt_pct = (wickets / balls) * 100
            
            stats_list.append({
                'Bowler': b_name,
                'Balls Faced': balls,
                'Strike Rate': sr,
                'Boundary %': boundary_pct,
                'Wicket %': wkt_pct,
                'Color': 'Selected' if b_name == bowler else 'Others'
            })

    scatter_df = pd.DataFrame(stats_list)

    if not scatter_df.empty:
        fig_scatter = px.scatter(
            scatter_df,
            x="Boundary %",
            y="Wicket %",
            size="Balls Faced",
            color="Color",
            hover_name="Bowler",
            color_discrete_map={'Selected': '#FF4B4B', 'Others': '#636EFA'},
            title=f"Scatter: Risk vs Reward ({batter})",
            labels={'Boundary %': 'Boundary Frequency (%)', 'Wicket %': 'Wicket Probability (%)'}
        )
        # Add reference lines
        fig_scatter.add_hline(y=scatter_df['Wicket %'].mean(), line_dash="dash", line_color="gray", annotation_text="Avg Wkt %")
        fig_scatter.add_vline(x=scatter_df['Boundary %'].mean(), line_dash="dash", line_color="gray", annotation_text="Avg Bndry %")
        fig_scatter.update_layout(template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)


    # --- SECTION 4: CONSISTENCY PLOT ---
    st.subheader("Match-by-Match Consistency")
    
    # Group by Match ID to separate meetings
    consistency = h2h.groupby('match_id').apply(lambda x: pd.Series({
        'SR': (x['batsman_runs'].sum() / len(x) * 100) if len(x) > 0 else 0,
        'Runs': x['batsman_runs'].sum(),
        'Balls': len(x)
    })).reset_index()

    # Just creating a sequential match number for the X-axis
    consistency['Match_Seq'] = range(1, len(consistency) + 1)

    fig_cons = go.Figure()
    fig_cons.add_trace(go.Scatter(
        x=consistency['Match_Seq'], 
        y=consistency['SR'],
        mode='lines+markers',
        name='Strike Rate',
        line=dict(color='#FFA500', width=3),
        text=consistency['Runs'].apply(lambda x: f"{x} runs"), # Hover text
        hovertemplate="Match %{x}<br>SR: %{y:.1f}<br>%{text}<extra></extra>"
    ))

    fig_cons.update_layout(
        title="Strike Rate Consistency (Across Matches)",
        xaxis_title="Meeting Number",
        yaxis_title="Strike Rate",
        template="plotly_dark"
    )
    st.plotly_chart(fig_cons, use_container_width=True)