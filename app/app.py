import streamlit as st
import plotly.graph_objects as go
from simulator import Simulation

def app():

    st.image("images/pgt-simulator-logo.png")
    tab1, tab2 = st.tabs(["App","Background"])
    with tab2:
        st.subheader("Background")
        info = """
                Coming soon.
                """
        st.markdown(info)
    with tab1:
        st.subheader("Simulation settings")
        st.warning(":exclamation: Plausible default settings and guidance based on previous research to follow :exclamation:")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Physiological/treatment parameters**")
            aneuploidy_help = "The percentage of embryos that are aneuploid, and have a 0% chance of resulting in a live birth"
            aneuploidy_rate = st.slider("Aneuploidy rate (%)",0,100,40,help=aneuploidy_help)
            lbr = st.slider("Live birth rate per embryo transfer (%)",0,100,40)
            embryo_help = """
                        The number of embryos available for transfer over each complete cycle.
                        We assume no fresh embryos are transferred.
                        """
            n_embryos = st.slider("Available (frozen) embryos per complete cycle",0,20,5,help=embryo_help)
        with cols[1]:
            st.markdown("**PGT-A detection and error rates**")
            tpr_help = "The probability an aneuploid embryo is correctly detected by PGT, and as a result not transferred."
            tpr = st.slider("True positive rate (sensitivity)",0.0,1.0,0.5,help=tpr_help)
            fpr_help = "The probability a normal embryo is incorrectly marked as aneuploid by PGT, and as a result not transferred."
            fpr = st.slider("False positive rate (1-specificity)",0.0,1.0,0.5,help=fpr_help)
        if st.button("Simulate"):
            
            # perform simulation
            sim = Simulation(n_embryos,aneuploidy_rate/100,lbr/100,tpr,fpr)
            sim.simulate(3,5000,5000)
            results_per_et = sim.get_summarised_results()
            results_per_complete = sim.get_summarised_results('complete_n')
            st.subheader("Results")
            st.markdown("Cumulative live birth rates after three complete cycles.")
            # per complete cycle
            plot_df_pgt = results_per_complete.loc[(results_per_complete.complete_n > 0) & (results_per_complete.pgt == True),:]
            plot_df_nopgt = results_per_complete.loc[(results_per_complete.complete_n > 0) & (results_per_complete.pgt == False),:]
            fig = go.Figure([go.Scatter(x=plot_df_pgt.complete_n, y=plot_df_pgt.clbr*100, mode='lines+markers',line=dict(shape='hv'),name='PGT'),
                            go.Scatter(x=plot_df_nopgt.complete_n, y=plot_df_nopgt.clbr*100, mode='lines+markers',line=dict(shape='hv'),name='No PGT')])
            fig.update_traces(hovertemplate="<br>".join(['Cycle: %{x}','CLBR: %{y:.1f}%']))
            fig.update_xaxes(tickvals=list(range(0,50,1)))
            fig.update_yaxes(tickvals=list(range(0,100,10)))
            fig.update_layout(height=300,
                    width=200,
                    showlegend=True,
                    title="Live birth rate per complete cycle",
                    xaxis=dict(
                        title="Complete cycle number",
                        tickfont = dict(size=16),
                        titlefont=dict(size=16)),
                    yaxis=dict(
                        title="Cumulative live birth rate (%)",
                        tickfont = dict(size=16),
                        titlefont=dict(size=16)),
                    margin=dict(l=0, r=0, t=20, b=0)            
                )
            st.plotly_chart(fig,
                                use_container_width=True,
                                config= dict(displayModeBar = False))

            # per embryo transfer
            plot_df_pgt = results_per_et.loc[(results_per_et.et_n > 0) & (results_per_et.pgt == True),:]
            plot_df_nopgt = results_per_et.loc[(results_per_et.et_n > 0) & (results_per_et.pgt == False),:]
            fig = go.Figure([go.Scatter(x=plot_df_pgt.et_n, y=plot_df_pgt.clbr*100, mode='lines+markers',line=dict(shape='hv'),name='PGT'),
                            go.Scatter(x=plot_df_nopgt.et_n, y=plot_df_nopgt.clbr*100, mode='lines+markers',line=dict(shape='hv'),name='No PGT')])
            fig.update_xaxes(tickvals=list(range(0,50,1)))
            fig.update_yaxes(tickvals=list(range(0,100,10)))
            fig.update_traces(hovertemplate="<br>".join(['Cycle: %{x}','CLBR: %{y:.1f}%']))
            fig.update_layout(height=300,
                    width=200,
                    showlegend=True,
                    title="Live birth rate per embryo transfer",
                    xaxis=dict(
                        title="Embryo transfer number",
                        tickfont = dict(size=16),
                        titlefont=dict(size=16)),
                    yaxis=dict(
                        title="Cumulative live birth rate (%)",
                        tickfont = dict(size=16),
                        titlefont=dict(size=16)),
                    margin=dict(l=0, r=0, t=20, b=0)            
                )
            st.plotly_chart(fig,
                                use_container_width=True,
                                config= dict(displayModeBar = False))

if __name__ == '__main__':
    app()