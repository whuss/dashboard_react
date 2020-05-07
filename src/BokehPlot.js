import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

function Plot(props) {
    const instance = useRef(null);

    const [{ data, isLoading, isError }, doFetch] = useDataApi(props.src, {});

    useEffect(() => {
        if (data) {
            const scriptTag = document.createElement("script");
            scriptTag.text = data.script;
            instance.current.appendChild(scriptTag);
        } else {
            console.log("Plot: deleted: ", props.src);
        }

        return () => {
            if (instance.current) {
                // Delete Bokeh script
                instance.current.innerHtml = "";
            }
        };
    }, [data]);

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
