import streamlit as st

st.set_page_config(page_title='경사하강법', page_icon='🧮')
st.title('🧮 경사하강법 기반 추세선 계산')

# 데이터 개수 입력
n = st.number_input(
    '데이터의 개수를 입력하시오:',
    min_value=1,
    value=3,
    step=1
)

data = []

# 데이터 입력
for i in range(n):
    x_value = st.number_input(
        f'{i+1}번째 데이터의 x값을 입력하시오:',
        min_value=0.0,
        value=0.0,
        format='%.2f',
    )

    y_value = st.number_input(
        f'{i+1}번째 데이터의 y값을 입력하시오:',
        min_value=0.0,
        value=0.0,
        format='%.2f',
    )

    data.append((x_value, y_value))

# 손실함수의 계수 계산
p = 0
q = 0
r = 0

for x_value, y_value in data:
    p += x_value ** 2
    q += -2 * x_value * y_value
    r += y_value ** 2

p = p / n
q = q / n
r = r / n

st.info(f'손실함수: E(a) = {p}a² - {-q}a + {r}')

# 학습 설정
a = st.number_input(
    '초깃값을 입력하시오:',
    value=0.0,
    format='%.2f'
)

eta = st.number_input(
    '학습률을 입력하시오:',
    min_value=0.0,
    value=0.01,
    format='%.2f'
)

if st.button('경사하강법 실행'):

    if p == 0:
        st.error('x값 중 적어도 하나는 0보다 커야 합니다.')

    elif eta == 0:
        st.error('학습률을 양수인 값으로 입력하시오.')

    elif eta >= 1 / p:
        st.error(f'학습률을 {1/p} 미만인 값으로 입력하시오.')

    else:
        cnt = 0
        converged = False

        # 초기 상태 기록: (반복 횟수, 기울기, 손실값)
        loss = sum((y - a * x) ** 2 for x, y in data) / n
        history = [(cnt, a, loss)]

        # 경사하강법
        while cnt < 100000:

            if abs(2 * p * a + q) < 0.00001:
                converged = True
                break

            a = a - eta * (2 * p * a + q)
            cnt += 1

            # 업데이트 이후의 상태 기록
            loss = sum((a * x - y) ** 2 for x, y in data) / n
            history.append((cnt, a, loss))

        # 마지막 업데이트 이후에도 수렴 여부 확인
        if abs(2 * p * a + q) < 0.00001:
            converged = True

        if converged:
            st.success('경사하강법이 종료 기준을 만족하여 수렴하였습니다.')
            st.success(f'총 업데이트 횟수: {cnt}번')
            st.success(f'최종 추세선: f(x) = {a}x')
        
            # 그래프 범위 설정
            a_min = min(min(a for cnt, a, loss in history), -q / (2 * p)) - 1
            a_max = max(max(a for cnt, a, loss in history), -q / (2 * p)) + 1
    
            # 손실함수 곡선을 그릴 기울기 값
            a_values = [
                a_min + (a_max - a_min) * i / 500
                for i in range(501)
            ]
    
            fig = go.Figure()
    
            # 손실함수 E(a) = pa² + qa + r
            fig.add_trace(go.Scatter(
                x=a_values,
                y=[p * a ** 2 + q * a + r for a in a_values],
                mode='lines',
                name='손실함수 E(a)',
                line=dict(color='royalblue'),
                hovertemplate=(
                    '기울기 a: %{x:.6f}<br>'
                    '손실값 E(a): %{y:.6g}<extra></extra>'
                )
            ))
    
            # history에 저장된 업데이트 이후의 점들
            fig.add_trace(go.Scatter(
                x=[a for cnt, a, loss in history[1:]],
                y=[loss for cnt, a, loss in history[1:]],
                customdata=[cnt for cnt, a, loss in history[1:]],
                mode='markers',
                name='업데이트된 점',
                marker=dict(color='orange', size=8),
                hovertemplate=(
                    '업데이트 횟수: %{customdata}번<br>'
                    '기울기 a: %{x:.6f}<br>'
                    '손실값 E(a): %{y:.6g}<extra></extra>'
                )
            ))
    
            # 초기점: history의 첫 번째 기록
            fig.add_trace(go.Scatter(
                x=[history[0][1]],
                y=[history[0][2]],
                mode='markers',
                name='초기점 (0회)',
                marker=dict(color='green', size=12, symbol='diamond'),
                hovertemplate=(
                    '초기점 (0회)<br>'
                    '기울기 a: %{x:.6f}<br>'
                    '손실값 E(a): %{y:.6g}<extra></extra>'
                )
            ))
    
            # 마지막 점: history의 마지막 기록
            fig.add_trace(go.Scatter(
                x=[history[-1][1]],
                y=[history[-1][2]],
                customdata=[history[-1][0]],
                mode='markers',
                name='마지막 점',
                marker=dict(color='red', size=12, symbol='x'),
                hovertemplate=(
                    '업데이트 횟수: %{customdata}번<br>'
                    '기울기 a: %{x:.6f}<br>'
                    '손실값 E(a): %{y:.6g}<extra></extra>'
                )
            ))
    
            fig.update_layout(
                title='손실함수와 경사하강법 업데이트',
                xaxis_title='기울기 a',
                yaxis_title='손실값 E(a)',
                template='plotly_white'
            )
    
            st.plotly_chart(fig)
    
            st.caption(
                '점들이 겹쳐 보이면 해당 영역을 드래그하여 확대하세요.'
            )
        else:
            st.warning('최대 반복 횟수에 도달했으나 종료 기준을 만족하지 못했습니다.')
