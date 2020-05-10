import React, { useEffect, useRef } from "react";

import { LoadingAnimation } from "./Toolbar";

import useDataApi from "./Fetch";

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
