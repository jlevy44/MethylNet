from umap import UMAP
import plotly.graph_objs as go
import plotly.offline as py
import pandas as pd
import numpy as np
import networkx as nx
import click
import pickle

CONTEXT_SETTINGS = dict(help_option_names=['-h','--help'], max_content_width=90)

@click.group(context_settings= CONTEXT_SETTINGS)
@click.version_option(version='0.1')
def visualize():
    pass

def umap_embed(beta_df, outcome_col, n_neighbors):
    umap=UMAP(n_components=3, random_state=42, n_neighbors=n_neighbors, min_dist=0.1)
    t_data=pd.DataFrame(umap.fit_transform(beta_df),index=beta_df.index,columns=['x','y','z'])
    t_data['color']=outcome_col
    return t_data

def plotly_plot(t_data_df, output_fname, G=None, axes_off=False):
    plots = []
    if t_data_df['color'].dtype == np.float64:
        plots.append(
            go.Scatter3d(x=t_data_df['x'], y=t_data_df['y'],
                         z=t_data_df['z'],
                         name='', mode='markers',
                         marker=dict(color=t_data_df['color'], size=2, colorscale='Viridis',
                         colorbar=dict(title='Colorbar')), text=t_data_df['color'] if 'name' not in list(t_data_df) else t_data_df['name']))
    else:
        colors = t_data_df['color'].unique()
        c = ['hsl(' + str(h) + ',50%' + ',50%)' for h in np.linspace(0, 360, len(colors) + 2)]
        color_dict = {name: c[i] for i,name in enumerate(sorted(colors))}

        for name,col in color_dict.items():
            plots.append(
                go.Scatter3d(x=t_data_df['x'][t_data_df['color']==name], y=t_data_df['y'][t_data_df['color']==name],
                             z=t_data_df['z'][t_data_df['color']==name],
                             name=str(name), mode='markers',
                             marker=dict(color=col, size=4), text=t_data_df.index[t_data_df['color']==name] if 'name' not in list(t_data_df) else t_data_df['name'][t_data_df['color']==name]))
        if G is not None:
            #pos = nx.spring_layout(G,dim=3,iterations=0,pos={i: tuple(t_data.loc[i,['x','y','z']]) for i in range(len(t_data))})
            Xed, Yed, Zed = [], [], []
            for edge in G.edges():
                if edge[0] in t_data_df.index.values and edge[1] in t_data_df.index.values:
                    Xed += [t_data_df.loc[edge[0],'x'], t_data_df.loc[edge[1],'x'], None]
                    Yed += [t_data_df.loc[edge[0],'y'], t_data_df.loc[edge[1],'y'], None]
                    Zed += [t_data_df.loc[edge[0],'z'], t_data_df.loc[edge[1],'z'], None]
            plots.append(go.Scatter3d(x=Xed,
                      y=Yed,
                      z=Zed,
                      mode='lines',
                      #line=go.scatter.Line(color='rgb(210,210,210)', width=10),
                      hoverinfo='none'
                      ))
            #print(Xed, Yed, Zed)
            #print(t_data[['x','y','z']])
    if axes_off:
        fig = go.Figure(data=plots,layout=go.Layout(scene=dict(xaxis=dict(title='',autorange=True,showgrid=False,zeroline=False,showline=False,ticks='',showticklabels=False),
            yaxis=dict(title='',autorange=True,showgrid=False,zeroline=False,showline=False,ticks='',showticklabels=False),
            zaxis=dict(title='',autorange=True,showgrid=False,zeroline=False,showline=False,ticks='',showticklabels=False))))
    else:
        fig = go.Figure(data=plots)
    py.plot(fig, filename=output_fname, auto_open=False)

@visualize.command()
@click.option('-i', '--input_pkl', default='./final_preprocessed/methyl_array.pkl', help='Input database for beta and phenotype data.', type=click.Path(exists=False), show_default=True)
@click.option('-c', '--column_of_interest', default='disease', help='Column extract from phenotype data.', type=click.Path(exists=False), show_default=True)
@click.option('-o', '--output_file', default='./visualization.html', help='Output visualization.', type=click.Path(exists=False), show_default=True)
@click.option('-nn', '--n_neighbors', default=5, show_default=True, help='Number of neighbors UMAP.')
@click.option('-a', '--axes_off', is_flag=True, help='Whether to turn axes on or off.')
def transform_plot(input_pkl, column_of_interest, output_file, n_neighbors,axes_off):
    input_dict = pickle.load(open(input_pkl,'rb'))
    t_data = umap_embed(input_dict['beta'], input_dict['pheno'][column_of_interest], n_neighbors)
    plotly_plot(t_data, output_file, axes_off=axes_off)

#################

if __name__ == '__main__':
    visualize()
