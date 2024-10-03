SELECT
    item.id AS id,
    item.itemid AS name,
    item.purchasedescription as description,
    item.custitem_jls_item_image_url AS item_img
FROM
    item
WHERE
    item.manufacturer = LUMIEN LIGHTING