import streamlit as st
from scipy.stats import norm
import numpy as np
from streamlit_echarts import st_echarts

# Define Black-Scholes functions
N = norm.cdf

def BS_CALL(S, K, T, r, sigma):
    r = r/100
    sigma = sigma/100
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * N(d1) - K * np.exp(-r*T)* N(d2)

def BS_PUT(S, K, T, r, sigma):
    r = r/100
    sigma = sigma/100
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*N(-d2) - S*N(-d1)

# Function to switch views
def switch_view(view):
    st.session_state.view = view
    st.rerun()

# Initialize session state variables if they don't exist
if "view" not in st.session_state:
    st.session_state.view = "calculator"

# Get the current view
current_view = st.session_state.view

# Display the appropriate view
if current_view == "calculator":
    if st.button(':green[Visualize]'):
        switch_view("visualize")

    st.write("# Black Scholes Calculator")

    col1, col2 = st.columns(2)
    with col1:
        Stemp = st.number_input('Current Asset Price ($ USD): ', value=st.session_state.get("S", None), placeholder="Ex: 52.50", key="Stemp")
        Ttemp = st.number_input('Time to Expiry (Fractional Years): ', value=st.session_state.get("T", None), placeholder="Ex: .75", key="Ttemp") #in days, will be converted to fraction of year
        calc = st.button('Calculate Option Prices')
    with col2:
        Ktemp = st.number_input('Strike Price ($ USD): ', value=st.session_state.get("K", None), placeholder="Ex: 55.00", key="Ktemp")
        sigmatemp = st.number_input('Annualized Implied Volatility (%): ', value=st.session_state.get("sigma", None), placeholder="Ex: 27", step=.1, key="sigmatemp") #in percent, will be converted to decimal form
        rtemp = st.number_input('Risk Free Interest Rate (%): ', value=st.session_state.get("r", None), placeholder="Ex: 4.5", key="rtemp") #in percent, will be converted to decimal form

    if calc and Stemp is not None and Ktemp is not None and Ttemp is not None and rtemp is not None and sigmatemp is not None:
        st.session_state.S = Stemp
        st.session_state.T = Ttemp
        st.session_state.K = Ktemp
        st.session_state.sigma = sigmatemp
        st.session_state.r = rtemp
        call_price = BS_CALL(st.session_state.S, st.session_state.K, st.session_state.T, st.session_state.r, st.session_state.sigma)
        put_price = BS_PUT(st.session_state.S, st.session_state.K, st.session_state.T, st.session_state.r, st.session_state.sigma)
        st.write(f'For S={st.session_state.S}, K={st.session_state.K}, T={st.session_state.T}, sigma={st.session_state.sigma}, r={st.session_state.r}:')
        col3, col4 = st.columns(2)
        with col3:
            st.write(f'Call Option Price ($ USD): **:orange[{call_price:.2f}]**')
        with col4:
            st.write(f'Put Option Price ($ USD): **:orange[{put_price:.2f}]**')
    else:
      st.write(f'Enter Values for All Parameters.')

elif current_view == "visualize":
    if st.button(':blue[Calculator]'):
        switch_view("calculator")

    # Retrieve the values from session state
    S = st.session_state.get("S")
    K = st.session_state.get("K")
    T = st.session_state.get("T")
    sigma = st.session_state.get("sigma")
    r = st.session_state.get("r")

    #generating data
    if S is None or K is None or T is None or r is None or sigma is None:
        st.write('Visualizing Default Values, use Calculator to Input Custom Values. \nS=**:orange[52.50]**, K=**:orange[55.00]**, T=**:orange[.5]**, sigma=**:orange[27]**, r=**:orange[4.5]**')
        S = 52.5
        K = 55.0
        T = .5
        r = 4.5
        sigma = 27.0
    else:
        st.write(f'Visualizing Values: S=**:orange[{S}]**, K=**:orange[{K}]**, T=**:orange[{T}]**, sigma=**:orange[{sigma}]**, r=**:orange[{r}]**.')

    #generating data for visualizations
    kVals = np.arange(K-10, K+10, .5)
    kCalls = [BS_CALL(S, k, T, r, sigma) for k in kVals]
    kPuts = [BS_PUT(S, k, T, r, sigma) for k in kVals]
    kCallData = list(map(list, zip(kVals, kCalls)))
    kPutData = list(map(list, zip(kVals, kPuts)))

    sigVals = np.arange(sigma-15, sigma+15, .75)
    sigCalls = [BS_CALL(S, K, T, r, sig) for sig in sigVals]
    sigPuts = [BS_PUT(S, K, T, r, sig) for sig in sigVals]
    sigCallData = list(map(list, zip(sigVals, sigCalls)))
    sigPutData = list(map(list, zip(sigVals, sigPuts)))

    rVals = np.arange(0,r+5,.25)
    rCalls = [BS_CALL(S, K, T, rv, sigma) for rv in rVals]
    rPuts = [BS_PUT(S, K, T, rv, sigma) for rv in rVals]
    rCallData = list(map(list, zip(rVals, rCalls)))
    rPutData = list(map(list, zip(rVals, rPuts)))

    TVals = np.arange(T-.5,T+.5,.025)
    TCalls = [BS_CALL(S, K, t, r, sigma) for t in TVals]
    TPuts = [BS_PUT(S, K, t, r, sigma) for t in TVals]
    TCallData = list(map(list, zip(TVals, TCalls)))
    TPutData = list(map(list, zip(TVals, TPuts)))

    st.write("# Option Pricing Visualized")
    data = [
        kCallData,
        kPutData,
        sigCallData,
        sigPutData,
        TCallData,
        TPutData,
        rCallData,
        rPutData,
    ]

    option = {
        "title": {"text": "How Are Option Prices Affected by Changes in Parameters?", "left": "center", "top": 0},
        "grid": [
            {"left": "7%", "top": "7%", "width": "38%", "height": "38%"},
            {"right": "7%", "top": "7%", "width": "38%", "height": "38%"},
            {"left": "7%", "bottom": "5%", "width": "38%", "height": "38%"},
            {"right": "7%", "bottom": "5%", "width": "38%", "height": "38%"},
        ],
        "tooltip": {"trigger": "axis",},
        "xAxis": [
            {"gridIndex": 0, "min": max(0,K-10), "max": K+10, "name": "Strike Price ($ USD)", "nameLocation": "middle"},
            {"gridIndex": 1, "min": max(0,sigma-15), "max": sigma+15, "name": "Implied Volatility (%)", "nameLocation": "middle"},
            {"gridIndex": 2, "min": max(0, T-.5), "max": T+.5, "name": "Time to Expiry (Years)", "nameLocation": "middle"},
            {"gridIndex": 3, "min": max(0, r-5), "max": r+5, "name": "Risk-Free Rate (%)", "nameLocation": "middle"},
        ],
        "yAxis": [
            {"gridIndex": 0, "min": max(0, int(min(kCalls[-1], kPuts[0]) - 2)), "max": int(max(kCalls[0], kPuts[-1]) + 2), "name": "Option Price (Premium) ($ USD)", "nameLocation": "middle"},
            {"gridIndex": 1, "min": max(0, int(min(sigCalls[0], sigPuts[0]) - 1)), "max": int(max(sigCalls[-1], sigPuts[-1]) + 1)},
            {"gridIndex": 2, "min": max(0, int(min(TCalls[0], TPuts[0]) - 1)), "max": int(max(TCalls[-1], TPuts[-1]) + 1)},
            {"gridIndex": 3, "min": max(0, int(min(rCalls[0], rPuts[-1]) - 1)), "max": int(max(rCalls[-1], rPuts[0]) + 1)},
        ],
        "series": [
            {
                "name": "Call Option",
                "type": "scatter",
                "xAxisIndex": 0,
                "yAxisIndex": 0,
                "markLine": {
                  "data": [
                    {"xAxis": K}
                  ],
                  "lineStyle": {"color": "orange", "type": "solid", "width": 2},
                  "label": {
                    "normal": {
                      "show": "false"
                    }
                  },
                  "symbol" : "none"
                },
                "data": data[0],
                "itemStyle": {"color": "#00ff00"},
            },
            {
                "name": "Put Option",
                "type": "scatter",
                "xAxisIndex": 0,
                "yAxisIndex": 0,
                "data": data[1],
                "itemStyle": {"color": "#ff0000"},
            },
            {
                "name": "Call Option",
                "type": "scatter",
                "xAxisIndex": 1,
                "yAxisIndex": 1,
                "markLine": {
                  "data": [
                    {"xAxis": sigma}
                  ],
                  "lineStyle": {"color": "#orange", "type": "solid", "width": 2},
                  "label": {
                    "normal": {
                      "show": "false"
                    }
                  },
                  "symbol" : "none"
                },
                "data": data[2],
                "itemStyle": {"color": "#00ff00"},
            },
            {
                "name": "Put Option",
                "type": "scatter",
                "xAxisIndex": 1,
                "yAxisIndex": 1,
                "data": data[3],
                "itemStyle": {"color": "#ff0000"}
            },
            {
                "name": "Call Option",
                "type": "scatter",
                "xAxisIndex": 2,
                "yAxisIndex": 2,
                "markLine": {
                  "data": [
                    {"xAxis": T}
                  ],
                  "lineStyle": {"color": "#orange", "type": "solid", "width": 2},
                  "label": {
                    "normal": {
                      "show": "false"
                    }
                  },
                  "symbol" : "none"
                },
                "data": data[4],
                "itemStyle": {"color": "#00ff00"},
            },
            {
                "name": "Put Option",
                "type": "scatter",
                "xAxisIndex": 2,
                "yAxisIndex": 2,
                "data": data[5],
                "itemStyle": {"color": "#ff0000"}
            },
                        {
                "name": "Call Option",
                "type": "scatter",
                "xAxisIndex": 3,
                "yAxisIndex": 3,
                "markLine": {
                  "data": [
                    {"xAxis": r}
                  ],
                  "lineStyle": {"color": "#orange", "type": "solid", "width": 2},
                  "label": {
                    "normal": {
                      "show": "false"
                    }
                  },
                  "symbol" : "none"
                },
                "data": data[6],
                "itemStyle": {"color": "#00ff00"},
            },
            {
                "name": "Put Option",
                "type": "scatter",
                "xAxisIndex": 3,
                "yAxisIndex": 3,
                "data": data[7],
                "itemStyle": {"color": "#ff0000"}
            },
        ],
        "title": [
        {"text": "Variable Strike Price", "left": "15%", "top": "0%"},
        {"text": "Variable Volatility", "left": "61%", "top": "0%"},
        {"text": "Variable Time to Expiry", "left": "12%", "top": "50%"},
        {"text": "Variable Risk-Free Rate", "left": "59%", "top": "50%"}
       ],
    }
    st_echarts(options=option, height="600px")
