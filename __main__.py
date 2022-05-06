"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources

# Add some constants
PATH_TO_STATIC_FILE = "static/index.html"
CONTENT_TYPE="text/html"

# Create an Azure Resource Group - it begins with 'rg_plmi_'
resource_group = resources.ResourceGroup('rg_plmi_')

# Create an Azure Storage Account - it begins with 'saplmi'
account = storage.StorageAccount(
    'saplmi',
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2,
    minimum_tls_version="TLS1_0"
    )

# Enable static website support
static_website = storage.StorageAccountStaticWebsite("staticWebsite",
    account_name=account.name,
    resource_group_name=resource_group.name,
    index_document=PATH_TO_STATIC_FILE)

# Upload the file to the storage account
index_html = storage.Blob(PATH_TO_STATIC_FILE,
    resource_group_name=resource_group.name,
    account_name=account.name,
    container_name=static_website.container_name,
    type="Block",
    source=pulumi.FileAsset(PATH_TO_STATIC_FILE),
    content_type=CONTENT_TYPE)


# Export the primary key of the Storage Account
primary_key = pulumi.Output.all(resource_group.name, account.name) \
    .apply(lambda args: storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1]
    )).apply(lambda accountKeys: accountKeys.keys[0].value)

# Export the endpoint of the Storage Account
pulumi.export("staticEndpoint", account.primary_endpoints.web)

pulumi.export("primary_storage_key", primary_key)
