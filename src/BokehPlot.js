import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

function Plot(props) {
    const instance = useRef(null);

    const [{ data, isLoading, isError }, doFetch] = useDataApi(props.src, {});

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
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <div>Loading ...</div> : addPlot(data)}
        </>
    );
}

export default Plot;
