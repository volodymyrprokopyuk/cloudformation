-- pirate_source
SELECT ingest.put_pirate_source(
    'PSRC001', 'GOOGLE', 'SEARCH_ENGINE', '2018-01-20 18:54:35+0200'
) pirate_source_id;
SELECT ingest.put_pirate_source(
    'PSRC002', 'FACEBOOK', 'SOCIAL_MEDIA', '2018-02-22 14:13:59+0200'
) pirate_source_id;
SELECT ingest.put_pirate_source(
    'PSRC003', 'TWITTER', 'SOCIAL_MEDIA', '2018-03-25 08:50:55+0200'
) pirate_source_id;
SELECT ingest.put_pirate_source(
    'PSRC003', 'TWITTER', 'SOCIAL_MEDIA', '2018-03-25 08:50:55+0200'
) pirate_source_id;

-- -- product
-- SELECT put_product(
--     'PROD001', 'Product title 1', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;
-- SELECT put_product(
--     'PROD002', 'Product title 2', '2019-02-06 21:34:54+0200',
--     '2019-03-06 21:34:54+0200', 'INACTIVE'
-- ) product_id;
-- SELECT put_product(
--     'PROD001', 'Product title 1 (updated)', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;

-- -- infringement
-- SELECT put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'ACTIVE'
-- ) infringement_id;
-- SELECT put_infringement(
--     'PROD002', 'PSRC002', '2019-05-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/2', 'TAKEN_DOWN'
-- ) infringement_id;
-- SELECT put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'TAKEN_DOWN'
-- ) infringement_id;
