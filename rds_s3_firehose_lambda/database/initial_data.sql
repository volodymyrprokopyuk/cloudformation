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
-- SELECT ingest.put_product(
--     'PROD001', 'Product title 1', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;
-- SELECT ingest.put_product(
--     'PROD002', 'Product title 2', '2019-02-06 21:34:54+0200',
--     '2019-03-06 21:34:54+0200', 'INACTIVE'
-- ) product_id;
-- SELECT ingest.put_product(
--     'PROD001', 'Product title 1 (updated)', '2019-01-06 21:34:54+0200',
--     '2019-02-06 21:34:54+0200', 'ACTIVE', 'https://api.movies.com/movies/1'
-- ) product_id;

-- -- infringement
-- SELECT ingest.put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'ACTIVE'
-- ) infringement_id;
-- SELECT ingest.put_infringement(
--     'PROD002', 'PSRC002', '2019-05-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/2', 'TAKEN_DOWN'
-- ) infringement_id;
-- SELECT ingest.put_infringement(
--     'PROD001', 'PSRC001', '2019-04-06 21:34:54+0200',
--     'https://www.pirate1.com/movies/1', 'TAKEN_DOWN'
-- ) infringement_id;

-- document_statictics
-- SELECT ingest.put_document_statistics(
--     'infringement/2019/07/05/08/infringement-ingest-DEV-InfringementDeliveryStream-1-2019-07-05-08-20-53-5c76ddb8-40ab-4312-95e0-c4286d629562',
--     'SUCCESS', 2, 2, 0
-- ) document_statistics_id;
-- SELECT ingest.put_document_statistics(
--     'Xproduct/2019/07/05/08/infringement-ingest-DEV-ProductDeliveryStream-1-2019-07-05-08-20-48-4be1357a-39b9-4990-819a-02b1f3f4e88d',
--     'FAILURE', 0, 0, 0, '{"error": "Downlaod document error"}'
-- ) document_statistics_id;
