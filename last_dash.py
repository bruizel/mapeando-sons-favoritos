import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import plotly.express as px
import pandas as pd

# Configurar usuário e chave da API
API_KEY = "00e4e3871a13b54eee91a384ebc33357"
USER = "burwalace"
PERIOD_OPTIONS = ["7day", "1month", "3month", "6month", "12month", "overall"]

# Criação do aplicativo Dash
app = dash.Dash(
        __name__,
        suppress_callback_exceptions=True
    )

app.layout = html.Div( # Organizar os componentes
    style={
        'backgroundColor': '#333',
        'color': '#FFF',
        'padding': '20px'
    },
    children=[
        html.H1("Top Músicas Mais Ouvidas"), # Título
        dcc.Dropdown( # Componente dropdown que permite ao usuário selecionar o período
            id='period-dropdown',
            options=[{'label': period, 'value': period} for period in PERIOD_OPTIONS], # Lista de opções, onde cada opção é um dicionário contendo um rótulo (label) e um valor (value)
            value='overall',  # Valor padrão para iniciar
            style={
                'backgroundColor': '#888',  # Cor de fundo do dropdown
                'color': '#555',
                'border': '1px solid #555'
            },
        ),
        dcc.Graph(id='top-music-graph', style={"height": "550px"}), # Gráfico músicas
        dcc.Graph(id='top-artist-graph', style={"height": "550px"})  # Gráfico artistas
    ]
)

@app.callback( # Atualiza o gráfico com base na interação do usuário
    Output('top-music-graph', 'figure'), # Atualiza o gráfico de musicas
    Output('top-artist-graph', 'figure'),  # Atualiza o gráfico de artistas
    Input('period-dropdown', 'value') # Valor selecionado no dropdown
)
def update_graph(selected_period): # Recebe periodo selecionado
    # Monta a URL da requisição
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={USER}&api_key={API_KEY}&format=json&period={selected_period}&limit=10"
    response = requests.get(url) # Armazena a resposta da requisição
    data = response.json() # Converte JSON

    # Tratar os dados com Pandas
    tracks = data.get("toptracks", {}).get("track", [])
    df = pd.DataFrame(tracks) # DataFrame com dados das faixas

    # Filtrar apenas colunas importantes
    df = df[["name", "artist", "playcount"]]
    df["artist"] = df["artist"].apply(lambda x: x["name"]) # Extrair nome do artista
    df["playcount"] = df["playcount"].astype(int) # Converter playcount para int

    # Verifica se há dados para exibir
    if df.empty:
        return (
            px.bar(title="Nenhum dado disponível para o período selecionado."),
            px.bar(title="Nenhum dado disponível para o período selecionado.")
        )

    # Criar gráfico de músicas
    fig_music = px.bar( # Barras
        df, # DataFrame
        x="playcount", # Eixo X
        y="name", # Eixo Y
        orientation="h",
        color="playcount", # Cores com base no playcount 
        color_continuous_scale=px.colors.sequential.Viridis, # Esquema de cores
        labels={ # Rótulos para os eixos
            "playcount": "Número de vezes ouvida",
            "name": "Música",
        },
        title=f"Top 10 Músicas Mais Ouvidas - {selected_period}" # Título com o período selecionado
    )

    # Inverter a ordem para manter a mais tocada no topo
    fig_music.update_yaxes(categoryorder="total ascending")
    fig_music.update_layout(template="plotly_dark")

    # Agrupar por artista e somar playcount
    df_artist = df.groupby('artist', as_index=False).agg({'playcount': 'sum'})

    # Criar gráfico de artistas
    fig_artist = px.bar(
        df_artist,
        x="playcount",
        y="artist",
        orientation="h",
        color="playcount",
        color_continuous_scale=px.colors.sequential.Viridis,
        labels={
            "playcount": "Número de vezes ouvida",
            "artist": "Artista",
        },
        title=f"Top Artistas Mais Ouvidos - {selected_period}"
    )

    # Inverter a ordem para manter a mais tocada no topo
    fig_artist.update_yaxes(categoryorder="total ascending")
    fig_artist.update_layout(template="plotly_dark")

    # Exibe os gráficos
    return fig_music, fig_artist  # Retorna ambos os gráficos

# Executa a aplicação
if __name__ == '__main__':
    app.run_server(debug=True)
