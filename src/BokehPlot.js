import React, { Component, useState, useEffect, useRef } from "react";
//import ScriptTag from "react-script-tag";

function Plot(props) {
    const instance = useRef(null);

    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [plot, setPlot] = useState(null);

    useEffect(() => {
        fetch(props.src)
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setPlot(result);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            );

        return () => {
            setPlot(null);
        };
    }, []);

    useEffect(() => {
        if (plot)
        {
            console.log("Plot: fully loaded: ", plot);
            const scriptTag = document.createElement("script");
            scriptTag.text = plot.script;
            instance.current.appendChild(scriptTag);
        }
        else
        {
            console.log("Plot: deleted: ", props.src);
        }
    }, [plot]);

    useEffect(() => {
        console.log("Plot: src changed: ", props.src);
    }, [props.src]);

    if (error) {
        return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
        return <div>Loading ...</div>;
    } else if (plot) {
        return (
            <>
                {/* <ScriptTag type="text/javascript">{plot.script}</ScriptTag> */}
                <div className={plot.class} id={plot.id} data-root-id={plot.data_root_id}></div>
                <div ref={instance} />
            </>
        );
    } else {
        return <div>Plot is null</div>;
    }
}

function PlotDevice(props) {
    const instance = useRef(null);

    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [plot, setPlot] = useState(null);

    useEffect(() => {
        const url = props.src + "/" + props.device;
        console.log("Plot: fetch url: ", url);
        fetch(url)
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setPlot(result);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            );

        return () => {
            setPlot(null);
        };
    }, []);

    useEffect(() => {
        if (plot)
        {
            console.log("Plot: fully loaded: ", plot);
            const scriptTag = document.createElement("script");
            scriptTag.text = plot.script;
            instance.current.appendChild(scriptTag);
        }
        else
        {
            console.log("Plot: deleted: ", props.src);
        }
    }, [plot]);

    useEffect(() => {
        console.log("Plot: src changed: ", props.src);
    }, [props.src]);

    if (error) {
        return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
        return <div>Loading ...</div>;
    } else if (plot) {
        return (
            <>
                {/* <ScriptTag type="text/javascript">{plot.script}</ScriptTag> */}
                <div align="center">
                    <div className={plot.class} id={plot.id} data-root-id={plot.data_root_id}></div>
                </div>
                <div ref={instance} />
            </>
        );
    } else {
        return <div>Plot is null</div>;
    }
}

export {Plot, PlotDevice};