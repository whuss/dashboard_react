import React from "react";

import Pagination from "react-bootstrap/Pagination";

interface PaginationInterface {
    current_page: number,
    num_pages: number,
    has_next: boolean,
    has_prev: boolean,
    next_num: number,
    prev_num: number,
    pages: (number|null)[],
}

interface PaginationBarProps {
    pagination?: PaginationInterface,
    setPage: (page: number) => void
}

function PaginationBar(props: PaginationBarProps) {
    const pagination = props.pagination;
    const setPage = props.setPage;

    if (!pagination) {
        return <></>;
    }

    const { current_page, num_pages, has_next, has_prev, pages } = pagination;

    if (num_pages <= 1) {
        return <></>;
    }

    function clickPage(page: number) {
        console.log("click page: ", page);
        setPage(page);
    }

    function prevPage() {
        console.log("prev page");
        if (has_prev) {
            setPage(current_page - 1);
        }
    }

    function nextPage() {
        console.log("next page");
        if (has_next) {
            setPage(current_page + 1);
        }
    }

    function item(page: number|null) {
        if (page) {
            return (
                <Pagination.Item onClick={() => clickPage(page)} key={page} active={page === current_page}>
                    {page}
                </Pagination.Item>
            );
        }
        return (
            <Pagination.Item key="ellipsis" disabled={true} active={false}>
                &hellip;
            </Pagination.Item>
        );
    }

    return (
        <Pagination size="sm">
            <Pagination.Prev  onClick={() => prevPage()} disabled={!has_prev} />
            {pages.map((page) => item(page))}
            <Pagination.Next onClick={() => nextPage()} disabled={!has_next} />
        </Pagination>
    );
}


export default PaginationBar;
