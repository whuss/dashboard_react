import React, { useState, useEffect, useRef } from "react";

import { LoadingAnimation } from "./Toolbar";

import useDataApi, { usePostApi } from "./Fetch";

function plotUrl(plotname) {
    return `/backend/plot/${plotname}`;
}

function PlotNew(props) {
    const url = plotUrl(props.plot_name);
    const plot_parameters = props.plot_parameters;

    const instance = useRef(null);

    const [{ data, isLoading, isError, errorMsg }, doFetch] = usePostApi(url, plot_parameters);

    useEffect(() => {
        const scriptTag = document.createElement("script");
        const currentElement = instance.current;
        scriptTag.text = data.script;
        currentElement.appendChild(scriptTag);

        return () => {
            if (currentElement) {
                // Delete Bokeh script
                currentElement.innerHtml = "";
            }
        };
    }, [data]);

    useEffect(() => {
        doFetch(url, plot_parameters);
    }, [doFetch, url, plot_parameters]);

    const addPlot = (plot) => (
        <div align="center" ref={instance}>
            <div className={plot.class} id={plot.id} data-root-id={plot.data_root_id}></div>
        </div>
    );

    return <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>{addPlot(data)}</LoadingAnimation>;
}

function Plot(props) {
    const instance = useRef(null);

    const [{ data, isLoading, isError, errorMsg }, doFetch] = useDataApi(props.src, {});

    useEffect(() => {
        const scriptTag = document.createElement("script");
        const currentElement = instance.current;
        scriptTag.text = data.script;
        currentElement.appendChild(scriptTag);

        return () => {
            if (currentElement) {
                // Delete Bokeh script
                currentElement.innerHtml = "";
            }
        };
    }, [data]);

    useEffect(() => {
        doFetch(props.src);
    }, [doFetch, props.src]);

    const addPlot = (plot) => (
        <div align="center" ref={instance}>
            <div className={plot.class} id={plot.id} data-root-id={plot.data_root_id}></div>
        </div>
    );

    return <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>{addPlot(data)}</LoadingAnimation>;
}

function PlotData(props) {
    const instance = useRef(null);
    const data = props.data;

    useEffect(() => {
        const scriptTag = document.createElement("script");
        const currentElement = instance.current;
        scriptTag.text = data.script;
        currentElement.appendChild(scriptTag);

        return () => {
            if (currentElement) {
                // Delete Bokeh script
                currentElement.innerHtml = "";
            }
        };
    }, [data]);

    return (
        <>
        <div align="center" ref={instance}>
            <div className={data.class} id={data.id} data-root-id={data.data_root_id}></div>
        </div>
        </>
    );
}

function usePlot(plot_name, plot_parameters)
{
    const url = plotUrl(plot_name);
    const [{ data, isLoading, isError, errorMsg }, doFetch] = usePostApi(url, plot_parameters);

    const { plot, fields } = data;
    const plotElement = plot && <PlotData data={plot}/>;
    return [{fields, isLoading, isError, errorMsg}, plotElement];
}

export default Plot;
export { PlotData, PlotNew, usePlot, plotUrl };