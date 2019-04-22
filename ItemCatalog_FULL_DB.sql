--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6
-- Dumped by pg_dump version 11.2

-- Started on 2019-04-21 16:53:38

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2826 (class 0 OID 20412)
-- Dependencies: 197
-- Data for Name: appuser; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.appuser (userid, firstname, lastname, email) FROM stdin;
1	Savion	Jackson	savion.dev@gmail.com
2	Alexander	Jackson	savionjackson72@gmail.com
3	Saybo	Jackson	savionjobs@gmail.com
\.


--
-- TOC entry 2828 (class 0 OID 20422)
-- Dependencies: 199
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.category (categoryid, categoryname, description, dateadded, userid) FROM stdin;
1	Dogs	Dog breeds	2019-04-21 16:19:38.230576	1
2	Cats	Cat breeds	2019-04-21 16:19:38.246282	1
3	Birds	Bird breeds	2019-04-21 16:19:38.246282	1
4	Frogs	Kinds of Frogs	2019-04-21 16:19:38.246282	2
5	Lizards	Kinds of Lizards	2019-04-21 16:19:38.246282	2
6	Horses	Types of Horses	2019-04-21 16:19:38.246282	3
\.


--
-- TOC entry 2830 (class 0 OID 20435)
-- Dependencies: 201
-- Data for Name: categoryitems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categoryitems (itemid, itemname, description, dateadded, categoryid, userid) FROM stdin;
1	German Shepherd	medium to large-sized working dog that originated in Germany	2019-04-21 16:19:38.282931	1	1
2	Dobermann Pincher	medium-large breed of domestic dog that was originally developed around 1890	2019-04-21 16:19:38.293958	1	1
3	Border Collie	A remarkably bright workaholic	2019-04-21 16:19:38.293958	1	1
4	Poison Dart Frog	group of frogs native to tropical Central and South America	2019-04-21 16:19:38.293958	4	2
5	African Drawf Frog	aquatic frogs native to parts of Equatorial Africa	2019-04-21 16:19:38.302958	4	2
6	Mustang	free-roaming horse of the American west 	2019-04-21 16:19:38.302958	6	3
7	Clydesdale	a breed of draft horse named for and derived from the farm horses of Clydesdale, Scotland 	2019-04-21 16:19:38.311566	6	3
\.


--
-- TOC entry 2839 (class 0 OID 0)
-- Dependencies: 196
-- Name: appuser_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.appuser_userid_seq', 3, true);


--
-- TOC entry 2840 (class 0 OID 0)
-- Dependencies: 198
-- Name: category_categoryid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.category_categoryid_seq', 7, true);


--
-- TOC entry 2841 (class 0 OID 0)
-- Dependencies: 200
-- Name: categoryitems_itemid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categoryitems_itemid_seq', 8, true);


-- Completed on 2019-04-21 16:53:39

--
-- PostgreSQL database dump complete
--

