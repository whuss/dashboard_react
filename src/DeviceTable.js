import React from "react";

import useDataApi from "./Fetch";

function DeviceTable(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <div>Loading ...</div> : props.format_table(data)}
        </>
    );
}

export default DeviceTable;
