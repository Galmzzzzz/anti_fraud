--
-- PostgreSQL database dump
--

\restrict y59WdpFpki5sSsC6o1MKMDCufWUmg7vc4kHm1QluQsljJHWBdG5YKE1hOfb1aws

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: fraud_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fraud_reports (
    id bigint NOT NULL,
    transaction_id bigint NOT NULL,
    user_id bigint NOT NULL,
    detected_at timestamp with time zone DEFAULT now(),
    reason character varying(255),
    status character varying(32) DEFAULT 'open'::character varying
);


ALTER TABLE public.fraud_reports OWNER TO postgres;

--
-- Name: fraud_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fraud_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fraud_reports_id_seq OWNER TO postgres;

--
-- Name: fraud_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fraud_reports_id_seq OWNED BY public.fraud_reports.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id bigint NOT NULL,
    sender_id bigint NOT NULL,
    receiver_id bigint NOT NULL,
    sum bigint NOT NULL,
    status character varying(32) DEFAULT 'pending'::character varying,
    is_fraud boolean DEFAULT false,
    device_id bigint,
    user_ip character varying(45),
    CONSTRAINT transactions_sum_check CHECK ((sum > 0))
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: user_devices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_devices (
    device_id bigint NOT NULL,
    device character varying(65) NOT NULL,
    user_ip character varying(45) NOT NULL,
    user_id bigint NOT NULL,
    screen_width bigint,
    screen_height bigint
);


ALTER TABLE public.user_devices OWNER TO postgres;

--
-- Name: user_devices_device_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_devices_device_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_devices_device_id_seq OWNER TO postgres;

--
-- Name: user_devices_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_devices_device_id_seq OWNED BY public.user_devices.device_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    phone_number bigint NOT NULL,
    balance bigint DEFAULT 0 NOT NULL,
    password character varying(256) NOT NULL,
    ip character varying(45) NOT NULL,
    country character varying(64) DEFAULT 'unknown'::character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: fraud_reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fraud_reports ALTER COLUMN id SET DEFAULT nextval('public.fraud_reports_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: user_devices device_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_devices ALTER COLUMN device_id SET DEFAULT nextval('public.user_devices_device_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: fraud_reports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fraud_reports (id, transaction_id, user_id, detected_at, reason, status) FROM stdin;
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transactions (id, sender_id, receiver_id, sum, status, is_fraud, device_id, user_ip) FROM stdin;
1	6	2	1	success	f	2	127.0.0.1
2	6	2	1	success	f	2	127.0.0.1
\.


--
-- Data for Name: user_devices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_devices (device_id, device, user_ip, user_id, screen_width, screen_height) FROM stdin;
1	iphone	127.0.0.1	2	800	600
2	iphone	127.0.0.1	6	800	600
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, phone_number, balance, password, ip, country) FROM stdin;
1	8705830292	1000	$argon2id$v=19$m=65536,t=3,p=4$CkFobS1lLIXwfu8dwzhnbA$TH2sPrpr9IB+FYCKSewgfxe1pqLirAQRV8W6sRp8ozM	127.0.0.1	US
3	87058302828	1000	$argon2id$v=19$m=65536,t=3,p=4$kfK+l/Iew7g35lyrtbYWIg$dsTBKFs2vV2RUp2T6/W3ZNk4F2QkAe6qPamSzZm7ekM	127.0.0.1	RU
5	87058301111	1000	$argon2id$v=19$m=65536,t=3,p=4$a+29l/Leu3cuBcA4J2QMQQ$8RxV/5KmJG79AUkb13q8qfN+YEOvD3c0BpkeqBVMYKU	127.0.0.1	US
2	87058302929	1002	$argon2id$v=19$m=65536,t=3,p=4$47x3DgEA4Byj1LqXMkbIGQ$ZBFWi6/40ylOb12kVJlgDvFjFgJOLw4Bc4V/IiyzVO0	127.0.0.1	CN
6	87058302626	998	gala	127.0.0.1	RU
\.


--
-- Name: fraud_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.fraud_reports_id_seq', 1, false);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transactions_id_seq', 2, true);


--
-- Name: user_devices_device_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_devices_device_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- Name: fraud_reports fraud_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fraud_reports
    ADD CONSTRAINT fraud_reports_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: user_devices user_devices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_devices
    ADD CONSTRAINT user_devices_pkey PRIMARY KEY (device_id);


--
-- Name: user_devices user_devices_user_id_device_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_devices
    ADD CONSTRAINT user_devices_user_id_device_key UNIQUE (user_id, device);


--
-- Name: users users_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_number_key UNIQUE (phone_number);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: fraud_reports fraud_reports_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fraud_reports
    ADD CONSTRAINT fraud_reports_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES public.transactions(id) ON DELETE CASCADE;


--
-- Name: fraud_reports fraud_reports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fraud_reports
    ADD CONSTRAINT fraud_reports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: transactions transactions_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.user_devices(device_id) ON DELETE SET NULL;


--
-- Name: transactions transactions_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: transactions transactions_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_devices user_devices_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_devices
    ADD CONSTRAINT user_devices_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict y59WdpFpki5sSsC6o1MKMDCufWUmg7vc4kHm1QluQsljJHWBdG5YKE1hOfb1aws

