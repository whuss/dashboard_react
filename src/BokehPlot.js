import React, { useState, useEffect, useRef } from "react";

import OverlayTrigger from "react-bootstrap/OverlayTrigger";
import Popover from "react-bootstrap/Popover";
import Button from "react-bootstrap/Button";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faExclamationTriangle } from "@fortawesome/free-solid-svg-icons";

import { LoadingAnimation } from "./Toolbar";

import useDataApi, { usePostApi } from "./Fetch";

function plotUrl(plotname, cached) {
    if (cached === false) {
        return `/backend/plot_uncached/${plotname}`;
    }
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

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
            {addPlot(data)}
        </LoadingAnimation>
    );
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

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
            {addPlot(data)}
        </LoadingAnimation>
    );
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

function PlotPng(props) {
    const png = props.png;
    return <img src={`data:image/png;charset=US-ASCII;base64,${png}`} alt="" />;
}

function plotDispatch(plot) {
    const { png } = plot;
    if (png) {
        return <PlotPng png={png} />;
    }
    return <PlotData data={plot} />;
}

function formatFetchError(errorMsg) {
    return (
        <>
            <span>Fetch error: </span>
            <pre>{errorMsg}</pre>
        </>
    );
}

function formatTracebackError(data) {
    const { error, plot_name, plot_parameters } = data;

    const popover = (
        <Popover id="popover-basic">
            <Popover.Title as="h3">Error in {plot_name}</Popover.Title>
            <Popover.Content>
                <div className="errorMsg">
                    <span>Device: {plot_parameters.device}</span>
                    <ul>
                        {Object.keys(plot_parameters).forEach((key) => (
                            <li key={key}>
                                `${key} = ${plot_parameters[key]}`
                            </li>
                        ))}
                    </ul>
                    <pre>{error}</pre>
                </div>
            </Popover.Content>
        </Popover>
    );

    const ErrorMsg = (
        <OverlayTrigger rootClose trigger="click" placement="bottom" overlay={popover}>
            <Button variant="danger" size="sm">
                <FontAwesomeIcon icon={faExclamationTriangle} />
            </Button>
        </OverlayTrigger>
    );

    return ErrorMsg;
}

function element(isError, errorMsg, data) {
    if (isError) {
        return formatFetchError(errorMsg);
    }

    // Check if plot contains an error message
    if (data && data.error) {
        return formatTracebackError(data);
    }

    return data && data.plot && plotDispatch(data.plot);
}

function usePlot(plot_name, initial_plot_parameters, cached) {
    const [plotParameters, setPlotParameters] = useState(initial_plot_parameters);
    const url = plotUrl(plot_name, cached);
    const [{ data, isLoading, isError, errorMsg }, doFetch] = usePostApi(url, plotParameters);

    const { plot, fields } = data;

    const plotElement = element(isError, errorMsg, data);

    useEffect(() => {
        doFetch(url, plotParameters);
    }, [url, plotParameters, doFetch]);

    return {flags: { fields, isLoading, isError, errorMsg },
            plot: plotElement,
            plotParameters,
            setPlotParameters};
}

export default Plot;
export { PlotData, PlotNew, usePlot, plotUrl };
