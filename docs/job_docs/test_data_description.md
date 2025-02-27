# Explanation of Fields in Your Circuit/Network Connection Data
This dataset represents network connections (circuits) in a system like Nautobot. Below is an explanation of each field:

## General Circuit Details
**id** → Unique identifier for the connection.
**name** → Name of the circuit/connection (e.g., "Sample Connection 1").
**name_prefix** → Prefix used for the connection name (e.g., "SC1").
**status** → The operational status of the circuit (e.g., "Active").
**status_id** → A numeric identifier for the status.
**type** → The type of service provided (e.g., "Internet").
**type_id** → A numeric identifier for the circuit type.
**vendor** → The provider of the connection (e.g., "Vendor Inc.").
**vendor_id** → A unique identifier for the vendor.

## Bandwidth & Connection Speed
**bandwidth_down** → Download speed in Mbps (e.g., 100).
**bandwidth_up** → Upload speed in Mbps (e.g., 50).
**bandwidth_string** → Human-readable representation of bandwidth (e.g., "100 Mbps").

## Cost & Financial Details
**cost_in** → Cost of incoming traffic in monetary units (e.g., 500).
**cost_out** → Cost of outgoing traffic in monetary units (e.g., 300).
**initial_cost** → One-time setup or installation cost (e.g., 1000).
**express_cost** → Additional express service cost if applicable (e.g., 100).
**dekningsbidrag** → Contribution margin, likely indicating profitability (e.g., 200).
**dekningsgrad** → Coverage percentage (e.g., 40).

## Dates & Timelines
**order_date** → Date the circuit was ordered (e.g., "2025-02-20T00:00:00Z").
**order_delivery_date** → Expected delivery date for the order (e.g., "2025-02-25T00:00:00Z").
**desired_delivery_date** → The customer's requested delivery date (e.g., "2025-03-01T00:00:00Z").
**install_date** → The date the circuit was installed (e.g., "2025-02-28T00:00:00Z").
**live_date** → The date the circuit became active (e.g., "2025-03-01T00:00:00Z").
**actually_delivery_date** → The actual delivery date of the connection (e.g., "2025-02-24T00:00:00Z").
**termination_date** → The date when the circuit is scheduled for termination (e.g., "2025-12-31T00:00:00Z").
**termination_order_date** → The date when the termination was requested (e.g., "2025-12-01T00:00:00Z").
**start_invoice_date** → The date when billing starts for this circuit (e.g., "2025-03-01T00:00:00Z").

## Geographic & Physical Location Details
**location** → Name of the location where the circuit is installed (e.g., "Oslo").
**location_id** → A unique identifier for the location (e.g., 101).
**location_type** → Type of location (e.g., "Office").

## Connection Points (POP - Points of Presence)
**pop_a_address_string** → Address of the A-side point of presence (POP) (e.g., "123 Main St, Oslo").
**pop_a_category** → Category of POP A (e.g., "Category A").
**pop_a_geo_string** → Geographical coordinates of POP A (latitude, longitude) (e.g., "59.9139,10.7522").
**pop_a_map_url** → URL to a map location for POP A (e.g., "https://maps.example.com/pop_a1").
**pop_a_room** → Room designation for POP A (e.g., "Room 101").
**pop_b_address_string** → Address of the B-side point of presence (POP) (e.g., "456 Secondary St, Oslo").
**pop_b_category** → Category of POP B (e.g., "Category B").
**pop_b_geo_string** → Geographical coordinates of POP B (e.g., "59.9140,10.7523").
**pop_b_map_url** → URL to a map location for POP B (e.g., "https://maps.example.com/pop_b1").
**pop_b_room** → Room designation for POP B (e.g., "Room 102").