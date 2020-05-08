import React, { useEffect } from "react";

import Toolbar, { useInput } from "./Toolbar";

import Spinner from "react-bootstrap/Spinner";

import useDataApi from "./Fetch";

function useDeviceFilter() {
    const [filterStr, setFilterStr] = useInput(useDeviceFilter.filter, {
        prepend: (
            <>
                <i className="fa fa-lightbulb-o" aria-hidden="true"></i>
                <span className="label">Filter:</span>
            </>
        ),
    });

    useEffect(() => {
        useDeviceFilter.filter = filterStr;
    }, [filterStr]);

    return [filterStr, setFilterStr];
}
useDeviceFilter.filter = "";

function DeviceTable(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);
    const [filterStr, setFilterStr] = useDeviceFilter();
    const devices = data;

    const selectedDevices = devices.filter((s) => s.includes(filterStr));
    return (
        <>
            <Toolbar>{setFilterStr}</Toolbar>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? (
                <Spinner animation="border" size="sm" variant="secondary" />
            ) : (
                <div>
                    {/* <ul>{selectedDevices.map((d)=><li>{d}</li>)}</ul> */}
                    {props.format_table(selectedDevices)}
                </div>
            )}
        </>
    );
}

export default DeviceTable;
