import streamlit as st
import plotly.graph_objects as go

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
        step=0.01,
        format='%.2f'
    )

    y_value = st.number_input(
        f'{i+1}번째 데이터의 y값을 입력하시오:',
        min_value=0.0,
        value=0.0,
        step=0.01,
        format='%.2f'
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

st.info(f'손실함수: E(a) = {p:.2f}a² - {-q:.2f}a + {r:.2f}')

# 학습 설정
a = st.number_input(
    '초깃값을 입력하시오:',
    value=0.0,
    step=0.01,
    format='%.2f'
)

eta = st.number_input(
    '학습률을 입력하시오:',
    min_value=0.0,
    value=0.01,
    step=0.01,
    format='%.2f'
)

if st.button('경사하강법 실행'):

    if p == 0:
        st.error('x값 중 적어도 하나는 0보다 커야 합니다.')

    elif eta <= 0:
        st.error('학습률을 양수인 값으로 입력하시오.')

    elif eta >= 1 / p:
        st.error('학습률이 너무 큽니다. 더 작은 양수를 입력하시오.')

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
        else:
            st.warning(
                '최대 반복 횟수에 도달했으나 종료 기준을 만족하지 못했습니다.'
            )
            st.stop()

        # 수렴한 경우에만 최종 결과 출력
        st.success(f'총 업데이트 횟수: {cnt}번, 최종 추세선: f(x) = {a:.2f}x')

        # 그래프 범위 설정
        a_min = min(min(a for cnt, a, loss in history), -q / (2 * p)) - 1
        a_max = max(max(a for cnt, a, loss in history), -q / (2 * p)) + 1

        # 포물선의 꼭짓점
        a_vertex = -q / (2 * p)
        loss_vertex = sum(
            (a_vertex * x - y) ** 2 for x, y in data
        ) / n

        # 표시 범위 양 끝의 손실값
        loss_left = sum(
            (a_min * x - y) ** 2 for x, y in data
        ) / n

        loss_right = sum(
            (a_max * x - y) ** 2 for x, y in data
        ) / n

        fig = go.Figure()

        # 이차함수를 2차 베지어 곡선으로 표현
        # M: 시작점
        # Q: 제어점과 끝점으로 정의하는 2차 곡선
        # 꼭짓점에서 접선이 수평이 되도록 제어점 설정
        fig.add_shape(
            type='path',
            path=(
                f'M {a_min},{loss_left} '
                f'Q {(a_min + a_vertex) / 2},{loss_vertex} '
                f'{a_vertex},{loss_vertex} '
                f'Q {(a_vertex + a_max) / 2},{loss_vertex} '
                f'{a_max},{loss_right}'
            ),
            xref='x',
            yref='y',
            line=dict(color='royalblue', width=2),
            layer='below',
            name='손실함수 E(a)',
            showlegend=True,
            legendrank=0
        )

        # 업데이트된 점들
        fig.add_trace(go.Scatter(
            x=[a for cnt, a, loss in history[1:]],
            y=[loss for cnt, a, loss in history[1:]],
            customdata=[cnt for cnt, a, loss in history[1:]],
            mode='markers',
            name='업데이트된 점',
            marker=dict(color='orange', size=9),
            hovertemplate=(
                '업데이트 횟수: %{customdata}번<br>'
                '기울기 a: %{x}<br>'
                '손실값 E(a): %{y}<extra></extra>'
            )
        ))

        # 초기점
        fig.add_trace(go.Scatter(
            x=[history[0][1]],
            y=[history[0][2]],
            mode='markers',
            name='초기점 (0회)',
            marker=dict(color='green', size=12, symbol='diamond'),
            hovertemplate=(
                '초기점 (0회)<br>'
                '기울기 a: %{x}<br>'
                '손실값 E(a): %{y}<extra></extra>'
            )
        ))

        # 마지막 점
        fig.add_trace(go.Scatter(
            x=[history[-1][1]],
            y=[history[-1][2]],
            customdata=[history[-1][0]],
            mode='markers',
            name='마지막 점',
            marker=dict(color='red', size=12, symbol='x'),
            hovertemplate=(
                '업데이트 횟수: %{customdata}번<br>'
                '기울기 a: %{x}<br>'
                '손실값 E(a): %{y}<extra></extra>'
            )
        ))

        # 포물선이 처음 화면에 충분히 보이도록 세로 범위 설정
        loss_margin = (
            max(loss_left, loss_right) - loss_vertex
        ) * 0.05

        fig.update_layout(
            title='손실함수와 경사하강법 업데이트',
            xaxis_title='기울기 a',
            yaxis_title='손실값 E(a)',
            template='plotly_white',
            height=600,
            dragmode='pan',
            hovermode='closest',
            xaxis=dict(
                range=[a_min, a_max]
            ),
            yaxis=dict(
                range=[
                    loss_vertex - loss_margin,
                    max(loss_left, loss_right) + loss_margin
                ]
            )
        )

        # 그래프 조작 설정
        st.plotly_chart(
            fig,
            config={
                'scrollZoom': True,
                'displayModeBar': True,
                'displaylogo': False,
                'doubleClick': 'reset',
                'modeBarButtonsToRemove': ['select2d', 'lasso2d']
            }
        )

        st.caption(
            '마우스 휠: 확대·축소 | 드래그: 그래프 이동 | '
            '상단 +/− 버튼: 확대·축소 | 더블클릭: 원래 범위로 복원'
        )
        
