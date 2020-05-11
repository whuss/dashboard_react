import React, { useEffect, useRef } from "react";

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

export default Plot;
export { PlotNew };