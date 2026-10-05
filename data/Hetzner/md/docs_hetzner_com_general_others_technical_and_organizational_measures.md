# Technical and Organizational Measures

Last change on 2025-04-01 • Created on 2025-02-19 • ID: GE-68A66

These measures are also mentioned in Appendix 2 of our [Data Protection Agreement (DPA)](https://www.hetzner.com/AV/DPA_en.pdf) and [here](https://www.hetzner.com/AV/TOM_en.pdf) .

The Technical and Organizational Measures (TOMs) are implemented to ensure an appropriate level of protection for personal data, particularly with regard to confidentiality, integrity, availability, and resilience of systems. Below, you will find detailed information about Hetzner's TOMs.

**For the next few sections of this article, the following is true:**

- **Dedicated servers/Cloud Servers** : You/the Client are completely responsible for the management, maintenance and security of the server.
- **Managed products** : For these products, we at Hetzner take responsibility for the maintenance, administration, and security of your systems.
- The following article outlines product-specific differences in certain measures. Regardless of this, our **internal systems** are also subject to the applicable technical and organizational measures.

## Physical access control

Physical access control defines who has physical access to a site, building, or room.

| Measures                                                                                                              | Data centers   | Admin buildings   |
|-----------------------------------------------------------------------------------------------------------------------|----------------|-------------------|
| Electronic access control system with logging                                                                         | ✓              | ✓                 |
| Documented distribution of access media                                                                               | ✓              | ✓                 |
| Comprehensive video monitoring                                                                                        | ✓              | ✓                 |
| Policy about how to handle visitors                                                                                   | ✓              | ✓                 |
| High security perimeter fencing (with anti-climbing and anti-tunneling protection) around the entire data center park | ✓              | NA                |
| Separate colocation area with lockable racks                                                                          | ✓              | NA                |

### TOMs details - Physical access control

**Electronic access control system with logging:** We strictly limit access to our data center parks, the data centers themselves, all other facilities and any administrative buildings. It is only possible to enter them via our access control system, which logs all access information.

**Documented distribution of access media:** We issue access media such as keys only to authorized employees, subcontractors, and colocation customers. There is documentation for every time we give one of these people access media to ensure complete traceability.

We centrally manage and regularly review the distribution of the access media and the access rights assigned to them. Colocation customers are responsible for managing and checking their own access media.

**Comprehensive video monitoring:** We continuously video monitor all relevant areas of our operations, including our high security perimeter fencing, access roads, entrances and exits, security airlocks, and server rooms. All movements are recorded and documented. We store and delete the video footage in accordance with our deletion plan.

In addition, we record images for all access attempts for our colocation customers (including entrances and exits and security airlocks). We log the images and relevant timestamps on our administration interface. The customer can also view these images.

**Policy about how to handle visitors:** We have a written policy for how we handle external visitors. This policy defines clear rules for how visitors should register for their visit, and get their visit authorized by us, about being escorted by our teammates during their visit, what kind of ID they may need for their visit, and what happens at the end of their visit. We familiarize first-time colocation visitors with these guidelines and any others relevant to them as part of their first visit.

**High security perimeter fencing (with anti-climbing and anti-tunneling protection) around the entire data center park:** All of our data center parks have high security perimeter fencing, which includes additional features to prevent intruders from climbing over or digging under the fencing.

**Separate colocation area with lockable racks:** The colocation area is physically separated from our internal areas. Colocation customers can lock their colocation racks.

## Electronic access control

The electronic access control defines who is allowed to log on to a system so that only authorized people have access to it.

### Unmanaged products

| Measures                                                                                                                                                                                                                                                                             | Colocation           | Dedicated servers    | Cloud servers        | Storage Boxes       | Object Storage      |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|----------------------|----------------------|---------------------|---------------------|
| Individual customer accounts with numerous management options and access to the administration interface                                                                                                                                                                             | ✓                    | ✓                    | ✓                    | ✓                   | ✓                   |
| Traceable access logs and change logs for customer accounts                                                                                                                                                                                                                          | ✓                    | ✓                    | ✓                    | ✓                   | ✓                   |
| Required passwords for customer accounts with defined minimum requirements                                                                                                                                                                                                           | ✓                    | ✓                    | ✓                    | ✓                   | ✓                   |
| Option for two-factor authentication (2FA) for customer accounts                                                                                                                                                                                                                     | ✓                    | ✓                    | ✓                    | ✓                   | ✓                   |
| Client has exclusive access to server                                                                                                                                                                                                                                                | ✓                    | ✓                    | ✓                    | NA  (see next line) | NA  (see next line) |
| Only authorized Hetzner employees have administrative access, within the scope of the agreed service; via multi-level authentication and cryptographic protection. Access done for tasks ranging from infrastructure maintenance to complete server management depending on product. | NA  (see prev. line) | NA  (see prev. line) | NA  (see prev. line) | ✓                   | ✓                   |
| Additional measures are the responsibility of the Client                                                                                                                                                                                                                             | ✓                    | ✓                    | ✓                    | ✓                   | ✓                   |

### Managed products

| Measures                                                                                                                                                                                                                                                                             | Managed servers     | Web hosting         | Storage Shares      |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|---------------------|---------------------|
| Individual customer accounts with numerous management options and access to the administration interface                                                                                                                                                                             | ✓                   | ✓                   | ✓                   |
| Traceable access logs and change logs for customer accounts                                                                                                                                                                                                                          | ✓                   | ✓                   | ✓                   |
| Required passwords for customer accounts with defined minimum requirements                                                                                                                                                                                                           | ✓                   | ✓                   | ✓                   |
| Option for two-factor authentication (2FA) for customer accounts                                                                                                                                                                                                                     | ✓                   | ✓                   | ✓                   |
| Client has exclusive access to server                                                                                                                                                                                                                                                | NA  (see next line) | NA  (see next line) | NA  (see next line) |
| Only authorized Hetzner employees have administrative access, within the scope of the agreed service; via multi-level authentication and cryptographic protection. Access done for tasks ranging from infrastructure maintenance to complete server management depending on product. | ✓                   | ✓                   | ✓                   |
| Additional measures are the responsibility of the Client                                                                                                                                                                                                                             | ✓                   | ✓                   | ✓                   |

### TOMs details - Electronic access control

**Individual customer accounts with numerous management options and access to the administration interface:** Our [customer account panel](https://accounts.hetzner.com/) is available to you so that you can manage your customer data. You can use this panel to, for example, change your postal address or to generate a one-time password (OTP) so you can verify your identification if you need telephone support. All data transferred to and from the interface is encrypted.

You can also use

[https://accounts.hetzner.com](https://accounts.hetzner.com/) to access the administration interfaces for any products you have with us.

**Traceable access logs and change logs for customer accounts:** Our log system saves logins and administrative changes within the customer account. We store and save these in accordance with our company deletion plan and in compliance with the GDPR.

**Required passwords for customer accounts with defined minimum requirements:** You as a customer must set a password when you create a customer account with us, and must follow the security guidelines we have defined for that password. You can change your password at any time on the administration interface.

**Option for two-factor authentication (2FA) for customer accounts:** You can activate two-factor authentication (2FA) on your account at any time to better protect it.

**Client has exclusive access to server:** Dedicated servers &amp; Cloud servers: Only the Client provides access to the server. In this way, the Client is also responsible for managing and implementing access control measures.

With our dedicated and cloud servers, you as the customer have the option of logging into your server via SSH from any location and, for example, doing maintenance work yourself on the server using the operating system that is installed on the server. Hetzner does not "see" or influence which applications or operations that you have set up on your server. The exception to this are applications or operations that we prohibit in our customer Terms and Conditions.

Relevant activities in the customer account and system-side security events are logged and stored and deleted in accordance with our GDPR-compliant deletion plan.

We give you a first-time access password when we commission your server. Once we send you this password, we ask you to change it immediately to make it a unique and secure password. We do not know your new password.

**Only authorized Hetzner employees have access within the scope of the agreed service via multi-level authentication and cryptographic protection:** (from pure infrastructure maintenance to complete server management, depending on the product) We strictly limit access to the servers only to authorized employees, and they may only access the servers within the scope of the agreed services. Access to servers takes place exclusively via a multi-level authentication process and is secured by cryptographic protection mechanisms. The type and scope of access varies depending on the product:

Managed servers: For managed servers, employees receive root access exclusively for maintenance and support purposes. They do not access stored customer data or content. Exception: Access is granted if the customer has explicitly approved it in advance, for example in the context of a support request.

Web hosting: Access is granted exclusively for platform and infrastructure maintenance. Employees do not access stored customer data or content. Exception: Access is granted if the customer has explicitly approved it in advance, for example in the context of a support request.

Storage Boxes, Storage Shares, and Object Storage: Access is granted exclusively for platform and infrastructure maintenance. Employees do not access stored customer data or content. Exception: Access is granted if the customer has explicitly approved it in advance, for example in the context of a support request.

## Internal access control

Internal access control defines which authorizations people have within a system. It defines what a user may see, change, or execute after accessing a system.

### Unmanaged products

| Measures                                                                              | Colocation              | Dedicated servers       | Cloud servers                                                                                | Storage Boxes                                 | Object Storage                                |
|---------------------------------------------------------------------------------------|-------------------------|-------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| Regular updates                                                                       | Client's responsibility | Client's responsibility | ✓  for the underlying cloud infrastructure                                                   | ✓                                             | ✓                                             |
| Audit-proof, binding authorization procedure based on a role and authorization policy | Client's responsibility | Client's responsibility | ✓  the cloud infrastructure is accessed;  for the virtual machine, the Client is responsible | ✓  for file access, the Client is responsible | ✓  for file access, the Client is responsible |
| Maintaining, securing, and updating transferred data/software                         | Client's responsibility | Client's responsibility | Client's responsibility                                                                      | Client's responsibility                       | Client's responsibility                       |
| Additional measures are the responsibility of the Client                              | ✓                       | ✓                       | ✓  regarding access to cloud servers                                                         | ✓                                             | ✓                                             |

### Managed products

| Measures                                                                              | Managed servers                               | Web hosting                                   | Storage Shares                                |
|---------------------------------------------------------------------------------------|-----------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| Regular updates                                                                       | ✓  for the underlying infrastructure          | ✓                                             | ✓                                             |
| Audit-proof, binding authorization procedure based on a role and authorization policy | ✓  for file access, the Client is responsible | ✓  for file access, the Client is responsible | ✓  for file access, the Client is responsible |
| Maintaining, securing, and updating transferred data/software                         | Client's responsibility                       | Client's responsibility                       | Client's responsibility                       |
| Additional measures are the responsibility of the Client                              | ✓                                             | ✓                                             | ✓                                             |

### TOMs details - Internal access control

**Regular updates:** Cloud servers: We perform routine security updates on the underlying cloud infrastructure so we can find and remove potential security vulnerabilities that bad actors may try to exploit.

Managed servers, web hosting, Storage Shares, Storage Boxes, Object Storage We perform routine security updates on these systems so we can find and remove potential security vulnerabilities that bad actors may try to exploit.

**Audit-proof, binding authorization procedure based on a role and authorization policy:** Cloud servers: Our employees gain access to the cloud infrastructure based on a defined approval process based on our documented roles and rights plan. The access authorizations are checked regularly and are only granted for the required period of time. Every time that access rights are granted, changed, or revoked, it is documented in a complete and traceable manner.

Managed servers, web hosting, Storage Shares, Storage Boxes, Object Storage: Our employees gain access to these systems based on a defined approval process based on our documented roles and rights plan. The access authorizations are checked regularly and are only granted for the required period of time. Every time that access rights are granted, changed, or revoked, it is documented in a complete and traceable manner.

## Transfer control

Transfer control includes measures and procedures that make sure that the use, access, and transport of physical data storage media are monitored and protected against unauthorized access.

The complete and non-recoverable deletion of data by our deletion process is regularly checked and confirmed by an external provider. You can access the verification report from our external service provider

[here](https://files.hetzner.com/docs/Protocol_for_Erasure_Verificationg_en.pdf)

### Unmanaged products

| Measures                                                                                                                            | Colocation              | Dedicated servers   | Cloud servers   | Storage Boxes   | Object Storage   |
|-------------------------------------------------------------------------------------------------------------------------------------|-------------------------|---------------------|-----------------|-----------------|------------------|
| Defined process for deleting data from storage drives after contract is complete; implemented differently depending on product type | Client's responsibility | ✓                   | ✓               | ✓               | ✓                |
| Storage drives are physically destroyed if data cannot be successfully erased                                                       | Client's responsibility | ✓                   | ✓               | ✓               | ✓                |
| Physical access to storage devices only in defined areas; transport across locations exclusively in locked transport boxes          | Client's responsibility | ✓                   | ✓               | ✓               | ✓                |

### Managed products

| Measures                                                                                                                            | Managed servers   | Web hosting   | Storage Shares   |
|-------------------------------------------------------------------------------------------------------------------------------------|-------------------|---------------|------------------|
| Defined process for deleting data from storage drives after contract is complete; implemented differently depending on product type | ✓                 | ✓             | ✓                |
| Storage drives are physically destroyed if data cannot be successfully erased                                                       | ✓                 | ✓             | ✓                |
| Physical access to storage devices only in defined areas; transport across locations exclusively in locked transport boxes          | ✓                 | ✓             | ✓                |

### TOMs details - Transfer control

**Defined process for deleting data from storage drives after contract is complete:** (Implemented differently depending on product type) Depending on which product of ours you have purchased, we use several different automated deletion processes. After we have made sure that data has been completely deleted from the storage device, we re-use the storage device.

Dedicated servers: With our dedicated servers, we perform a residual-free deletion using a hardware supported deletion method.

Cloud servers: With our Cloud Servers, the image is deleted as soon as you as the customer remove the server. Depending on how long you used the product, deletion may be delayed: products with a very short runtime can be deleted immediately or shortly thereafter. For products that were used for a longer period, the final deletion usually takes place within up to 48 hours. In justified exceptional cases (e.g., capacity bottlenecks or operational requirements), deletion may also occur earlier.

After the retention period has expired, the image is permanently removed using a hardware-supported deletion method. Each customer is assigned their own image. Therefore, it is not possible for other customers to restore your data.

If backups are booked, they are created daily. In addition, the customer can manually create snapshots at any time. A maximum of seven backups can exist. Older backups are deleted after a new backup has been created. If you cancel your server, all backups belonging to that server are deleted accordingly. It is possible to convert a backup into a separately booked snapshot.

Backups are tied to the respective server. When the server is cancelled, the associated backup images are deleted. Booked snapshots remain available even after the server has been cancelled.

Managed servers: Depending on which product you have purchased, we operate your managed server using underlying infrastructure based on our dedicated servers or on our Cloud environment. The deletion method, therefore, depends on what kind of underlying infrastructure your managed server runs on. (See the above information on Dedicated servers &amp; Cloud servers.)

Web hosting: For our web hosting packages, access to the product is blocked on the cancellation date. The data stored on the server is deleted 30 days after the cancellation date.

Domains with a fixed term are not renewed after expiration and expire automatically. Domains without a fixed term (e.g., .de, .at) are deleted on the cancellation date.

Storage Shares &amp; Storage Boxes: Storage Shares and Storage Boxes use their own ZFS dataset, which is erased when the instance is deleted. The freed-up storage space is then re-used in ZFS, and is overwritten with new data over time. Customers do not have access to the block level, so it is not possible to retrieve deleted blocks.

After you cancel a Storage Box, we wait 24 hours before ultimately deleting it. Storage Shares are different. When you delete a Storage Share, we keep it in a deactivated state for 30 days. After this period runs out, the relevant ZFS dataset and database are ultimately deleted. After that, it is not possible to restore them.

Backups created for Storage Shares are also deleted after 30 days.

Object Storage: Our system stores the data on a Ceph-based distributed system. This distributed storage system distributes the data redundantly across several physical drives and nodes. When data is deleted, this happens using the Ceph cluster, which ensures that the data is removed from all storage nodes. After the data deletion process has started, the data blocks are overwritten by the distributed system or erased from the cluster.

Because this system is based on distributed architecture, the data deletion process is asynchronous, but consistent, across all storage nodes.

**Storage drives are physically destroyed if data cannot be successfully erased:** If, when we review the wipe process, it becomes clear that we cannot guarantee that the data has been completely erased, we physically destroy the affected hardware at our data center in Falkenstein, Germany. When we transport the affected drives to Falkenstein, we store them in locked transport boxes.

We destroy hardware based on standards defined by ISO/IEC 21964. The shredders that we use meet protection class 2 and correspond to security level H4 for hard disks and E3 for electronic media.

## Isolation control

Measures for isolation control make sure that data for each different customer or application within a system is separated from each other when they are processed and stored.

### Unmanaged products

| Measures                                                 | Colocation              | Dedicated servers       | Cloud servers   | Storage Boxes   | Object Storage          |
|----------------------------------------------------------|-------------------------|-------------------------|-----------------|-----------------|-------------------------|
| Physical and logical separation of data                  | Client's responsibility | Client's responsibility | ✓               | ✓               | ✓                       |
| Physical and logical separation of backup data           | Client's responsibility | Client's responsibility | ✓               | NA              | Client's responsibility |
| Additional measures are the responsibility of the Client | ✓                       | ✓                       | ✓               | NA              | NA                      |

### Managed products

| Measures                                                 | Managed servers   | Web hosting   | Storage Shares   |
|----------------------------------------------------------|-------------------|---------------|------------------|
| Physical and logical separation of data                  | ✓                 | ✓             | ✓                |
| Physical and logical separation of backup data           | ✓                 | ✓             | ✓                |
| Additional measures are the responsibility of the Client | ✓                 | ✓             | ✓                |

### TOMs details - Isolation control

**Physical and logical separation of data:** Cloud servers, Managed servers, web hosting, Storage Shares, Storage Boxes, Object Storage: We store the data for these systems either physically (on separate data storage devices) or logically (using permission systems and virtualization), and it is separated from other data. This measure ensures that your data remains isolated, that no unauthorized access occurs, and that your data does not get mixed with other data.

**Physical and logical separation of backup data:** Cloud servers, Managed servers, web hosting, Storage Shares: With these systems, we also ensure strict separation when storing the data. We save backups on logically and/or physically separate systems.

Depending on the product, backups may be stored in a different fire compartment or at a different location. Since only one data center is operated in Hillsboro (USA) and Singapore, these locations are exceptions. In these cases, backups are stored in the same data center as the server from which they were created.

Customers have no influence on the storage location. However, if a product location within the EU has been selected, the backups will also remain within the EU.

## Pseudonymization

| Measures                                           | Colocation              | Dedicated servers       | Cloud servers           | Managed servers         | Web hosting             | Storage Shares          | Storage Boxes           | Object Storage          |
|----------------------------------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|
| Pseudonymization of data stored within the systems | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility |

## Confidentiality

Confidentiality measures make sure that personal data is protected from unauthorized access or disclosure while it is being processed and stored.

| Measures                                                                                                                                        | Implementation                                        |
|-------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| Hetzner employees sign an agreement before they begin doing any work with personal data and promise to comply with data protection regulations. | ✓                                                     |
| Confidentiality agreement and implementation of TOMs by external persons before starting their activities for Hetzner (if necessary)            | ✓                                                     |
| Hetzner employees regularly get training to raise awareness for and knowledge about data protection and information security.                   | ✓                                                     |
| Encryption options for data transfers  (Implemented differently depending on product type)                                                      | ✓                                                     |
| Encryption of Data (at rest)                                                                                                                    | Client's responsibility                               |
| Encryption of Backups (at rest)                                                                                                                 | Client's responsibility  Exception Managed Servers: ✓ |

### TOMs details - Confidentiality

**Hetzner employees sign an agreement before they begin doing any work with personal data and promise to comply with data protection regulations.** All Hetzner employees are instructed that they may only process the Client's personal data in accordance with the Client's instructions. Before they begin working with customers' personal data, they sign an agreement in which they promise to handle personal data in compliance with data protection regulations.

**Confidentiality agreement and implementation of TOMs by external persons before starting their activities for Hetzner (if necessary)** If necessary, external persons sign a confidentiality agreement (NDA) and confirm the implementation of TOMs before starting their activities for Hetzner.

Note: This may include, for example, consulting services. Subcontractors/subprocessors are not included here, as different regulations apply to them.

**Hetzner employees regularly get training to raise awareness for and knowledge about data protection and information security.** We teach our employees about data protection requirements before they start working with customers' personal data. In addition, all employees receive further and regular training courses so they are continuously aware of their responsibilities regarding data protection and data security. This training includes information about the Client's right to issue instructions about their personal data.

**Encryption options for data transfers:** Hetzner provides its customers with several encryption options for data transfers, which can change depending on the product. We specify which encryption options are available for each product in the service descriptions for the main contract.

**Encryption of Backups (at rest):** Managed Servers: Backups are stored encrypted at rest.

## Integrity

Data integrity measures make sure that data and systems remain complete, uncorrupted, and correct while they are being stored or transferred.

### Unmanaged products

| Measures                                                 | Colocation              | Dedicated servers       | Cloud servers           | Storage Boxes           | Object Storage          |
|----------------------------------------------------------|-------------------------|-------------------------|-------------------------|-------------------------|-------------------------|
| Changes to data are logged                               | Client's responsibility | Client's responsibility | Client's responsibility | ✓                       | ✓                       |
| Responsibility for entering and processing data          | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility | Client's responsibility |
| Virus scanner / Security tests                           | Client's responsibility | Client's responsibility | Client's responsibility | Rootkit tests           | -                       |
| Additional measures are the responsibility of the Client | ✓                       | ✓                       | ✓                       | ✓                       | ✓                       |

### Managed products

| Measures                                                 | Managed servers         | Web hosting             | Storage Shares          |
|----------------------------------------------------------|-------------------------|-------------------------|-------------------------|
| Changes to data are logged                               | ✓                       | ✓                       | ✓                       |
| Responsibility for entering and processing data          | Client's responsibility | Client's responsibility | Client's responsibility |
| Virus scanner / Security tests                           | ✓                       | ✓                       | Rootkit tests           |
| Additional measures are the responsibility of the Client | ✓                       | ✓                       | ✓                       |

### TOMs details - Integrity

**Changes to data are logged:** Managed servers, web hosting, Storage Shares, Storage Boxes: We log any changes to saved data with a timestamp in our file system.

Object Storage: We log any changes to saved data with a timestamp in our file system, or we indicate it using metadata related to objects. Objects can be protected against being overwritten by using versioning and access control lists (ACLs).

**Responsibility for entering and processing data:** Managed servers, web hosting, Storage Shares, Storage Boxes, Object Storage: You as the customer are solely responsible for entering and editing your data. This includes not only data saved on the servers but also any data that you have entered on your customer account.

**Virus scanner / Security tests:** Managed servers &amp; web hosting: We use a centrally managed virus scanner solution for our managed servers and web hosting products. This allows us to simplify and standardize the management for all clients and security threats and to detect and mitigate any potential threats as quickly as possible.

Storage Shares &amp; Storage Boxes: We perform rootkit checks for our Storage Boxes and Storage Shares. These checks look for any hidden malware (rootkits) in the system.

## Availability, resilience and network security

Availability measures focus on keeping the systems in continued working order. Resilience measures make sure that the data remains available even under exceptional circumstances. Network security includes measures to protect the network infrastructure from unauthorized access and attacks.

### Unmanaged products

| Measures                                       | Colocation                  | Dedicated servers       | Cloud servers                                                | Storage Boxes           | Object Storage          |
|------------------------------------------------|-----------------------------|-------------------------|--------------------------------------------------------------|-------------------------|-------------------------|
| **Operation and support**                      |                             |                         |                                                              |                         |                         |
| 24/7 technical support directly in data center | NA  remote hands on request | ✓                       | ✓                                                            | ✓                       | ✓                       |
| Escalation process for faults and emergencies  | See product description     | See product description | See product description                                      | See product description | See product description |
| Monitoring                                     | Client's responsibility     | Client's responsibility | ✓  for Host  -  Client's responsibility  for virtual machine | ✓                       | ✓                       |

| Measures                                                                                                          | Colocation   | Dedicated servers   | Cloud servers   | Storage Boxes   | Object Storage   |
|-------------------------------------------------------------------------------------------------------------------|--------------|---------------------|-----------------|-----------------|------------------|
| **Power supply, climatization and facility management**                                                           |              |                     |                 |                 |                  |
| Uninterruptible power supply using redundant UPSs and emergency power supply system                               | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Redundant power supply from the substation                                                                        | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Redundant and energy-efficient cooling using direct free cooling and climate controls                             | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Cold-aisle containment in above-average raised flooring                                                           | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Monitoring of process-relevant parameters via intelligent measurement, control, regulation, and monitoring system | ✓            | ✓                   | ✓               | ✓               | ✓                |
| **Fire protection**                                                                                               |              |                     |                 |                 |                  |
| Site-wide early warning fire system; direct connection to the local fire and rescue coordination center           | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Dynamic fire protection measures                                                                                  | ✓            | ✓                   | ✓               | ✓               | ✓                |
| Regular training for emergencies and fire protection                                                              | ✓            | ✓                   | ✓               | ✓               | ✓                |

| Measures                                                                                                 | Colocation              | Dedicated servers       | Cloud servers                                                         | Storage Boxes                                                      | Object Storage                                                       |
|----------------------------------------------------------------------------------------------------------|-------------------------|-------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|----------------------------------------------------------------------|
| **Network and attack protection**                                                                        |                         |                         |                                                                       |                                                                    |                                                                      |
| Redundant and highly available network infrastructure  99.9% network availability in accordance with GTC | ✓                       | ✓                       | ✓                                                                     | ✓                                                                  | ✓                                                                    |
| Continuously active DDoS recognition                                                                     | ✓                       | ✓                       | ✓                                                                     | ✓                                                                  | ✓                                                                    |
| Use of firewall and port management                                                                      | Client's responsibility | Client's responsibility | Client's responsibility                                               | ✓                                                                  | ✓                                                                    |
| Individually configured firewall                                                                         | NA                      | ✓                       | ✓                                                                     | NA  (see next line)                                                | ✓                                                                    |
| Hetzner-managed firewall with 24/7 monitoring                                                            | NA                      | NA  (see prev. line)    | NA  (see prev. line)                                                  | ✓                                                                  | NA  (see prev. line)                                                 |
| **Backup and system protection**                                                                         |                         |                         |                                                                       |                                                                    |                                                                      |
| Backup and recovery plan                                                                                 | Client's responsibility | Client's responsibility | Client's responsibility  Backups and snapshots can be added for a fee | Client's responsibility  Snapshots depending on purchased services | Client's responsibility  Redundant storage within the cluster system |
| Disk mirroring                                                                                           | Client's responsibility | Client's responsibility | Client's responsibility                                               | ✓                                                                  | ✓                                                                    |

### Managed products

| Measures                                                                                                          | Managed servers                            | Web hosting             | Storage Shares            |
|-------------------------------------------------------------------------------------------------------------------|--------------------------------------------|-------------------------|---------------------------|
| **Operation and support**                                                                                         |                                            |                         |                           |
| 24/7 technical support directly in data center                                                                    | ✓                                          | ✓                       | ✓                         |
| Escalation process for faults and emergencies                                                                     | See product description                    | See product description | See product description   |
| Monitoring                                                                                                        | ✓                                          | ✓                       | ✓                         |
| **Power supply, climatization and facility management**                                                           |                                            |                         |                           |
| Uninterruptible power supply using redundant UPSs and emergency power supply system                               | ✓                                          | ✓                       | ✓                         |
| Redundant power supply from the substation                                                                        | ✓                                          | ✓                       | ✓                         |
| Redundant and energy-efficient cooling using direct free cooling and climate controls                             | ✓                                          | ✓                       | ✓                         |
| Cold-aisle containment in above-average raised flooring                                                           | ✓                                          | ✓                       | ✓                         |
| Monitoring of process-relevant parameters via intelligent measurement, control, regulation, and monitoring system | ✓                                          | ✓                       | ✓                         |
| **Fire protection**                                                                                               |                                            |                         |                           |
| Site-wide early warning fire system; direct connection to the local fire and rescue coordination center           | ✓                                          | ✓                       | ✓                         |
| Dynamic fire protection measures                                                                                  | ✓                                          | ✓                       | ✓                         |
| Regular training for emergencies and fire protection                                                              | ✓                                          | ✓                       | ✓                         |
| **Network and attack protection**                                                                                 |                                            |                         |                           |
| Redundant and highly available network infrastructure  99.9% network availability in accordance with GTC          | ✓                                          | ✓                       | ✓                         |
| Continuously active DDoS recognition                                                                              | ✓                                          | ✓                       | ✓                         |
| Use of firewall and port management                                                                               | ✓                                          | ✓                       | ✓                         |
| Individually configured firewall                                                                                  | NA  (see next line)                        | NA  (see next line)     | NA  (see next line)       |
| Hetzner-managed firewall with 24/7 monitoring                                                                     | ✓                                          | ✓                       | ✓                         |
| **Backup and system protection**                                                                                  |                                            |                         |                           |
| Backup and recovery plan                                                                                          | ✓  partially depends on purchased services | ✓                       | ✓  own backup recommended |
| Disk mirroring                                                                                                    | ✓                                          | ✓                       | ✓                         |

### TOMs details - Availability, resilience and network security

Availability measures focus on ensuring the continuous operation of systems. Resilience ensures that availability is maintained even under exceptional circumstances. Network security includes measures designed to protect the network infrastructure from unauthorized access and attacks.

## Operation and support

### 24/7 technical support directly in the data center

Our data centers are staffed 24/7/365 by our own technical support employees. This allows us to provide rapid on-site assistance, for example in the event of hardware failures. For more complex technical matters and non-technical issues, our specialized departments are available during regular business hours.

### Escalation process for faults and emergencies

Defined escalation processes are in place for faults and emergency situations. Depending on the respective product, incidents are handled in accordance with the applicable product description.

### Monitoring

Cloud servers: We continuously monitor the physical server (host) to ensure stable operation and performance. Our monitoring systems detect anomalies or failures in real time and notify the responsible team so that issues can be resolved promptly.

The Client is responsible for monitoring the virtual machine.

Managed servers, web hosting, Storage Shares, Storage Boxes, Object Storage: We continuously monitor all servers for these systems to ensure stable operation and performance. Our monitoring systems detect anomalies or failures in real time and notify the responsible team so that issues can be resolved promptly.

## Power supply, climatization and facility management

### Uninterruptible power supply using redundant UPS and emergency power supply system

Our uninterruptible power supply (UPS) guarantees a constant and uninterrupted power supply even in the event of a power outage. The UPS system provides temporary power until the regular power supply is restored or until the emergency power supply system becomes active. The modular UPS systems are designed with internal N+1 redundancy and are connected to two separate power distribution paths. In addition, the UPS systems are connected to a battery supply that can maintain operation for approximately 15 minutes.

The emergency power supply system provides long-term power in the event of a grid outage. This system is powered by diesel generators, enabling autonomous operation during longer power outages. Each data center building has its own emergency power supply system. A central main tank per row of data center buildings automatically supplies fuel to the emergency power supply tanks. The fuel level is continuously monitored and refilled if necessary. The stored fuel supply is sufficient to operate the data center autonomously for approximately three days.

In addition, grounding and equipotential bonding in our data centers are implemented in accordance with applicable standards to safely dissipate electrical disturbances.

### Redundant power supply from the substation

Power is supplied via redundant feeds from the substation. The feeds are designed in such a way that maintenance work or faults on one feed do not interrupt operations.

### Redundant and energy-efficient cooling using direct free cooling and climate controls

We use environmentally friendly and efficient cooling in our data centers by means of direct free cooling. This system uses outside air to regulate the temperature in the data centers and significantly reduces energy consumption. The N+2 redundancy ensures that additional cooling units are available to maintain continuous cooling even in the event of a fault.

Our raised floors are higher than average, providing additional space for optimized air circulation. This enables efficient distribution of cooled air and effective removal of heat.

### Cold-aisle containment in above-average raised flooring

Cold-aisle containment prevents cold and warm air from mixing by directing the cooled airflow specifically to the IT components. This increases the efficiency of the cooling system and minimizes energy consumption.

### Monitoring of process-relevant parameters via intelligent measurement, control, regulation, and monitoring system

All process-relevant operating parameters are continuously monitored via a central measurement, control, regulation, and monitoring system. Deviations are automatically detected in real time and trigger alerts, allowing prompt countermeasures to be taken. This monitoring significantly contributes to the stability and availability of the infrastructure.

## Fire protection

### Site-wide early warning fire system; direct connection to the local fire and rescue coordination center

Our data centers are equipped with an early fire detection system based on an aspirating smoke detection system. The fire alarm system is directly connected to the local fire and rescue coordination center. In addition, the system is integrated into our internal monitoring system, which monitors disruptions and triggers internal alerts.

Furthermore, each data center building is equipped with CO₂ handheld fire extinguishers and mobile CO₂ fire extinguishers to enable quick and effective response in emergencies.

### Dynamic fire protection measures

Fire protection areas in our data centers are separated by fire doors. These doors have an automatic closing function that is activated in the event of smoke detection in order to prevent rapid spread of fire.

To prevent fire spread between data center units, intermediate corridors are integrated as structural separation. Transformers, medium-voltage stations, and battery rooms are additionally protected by fire walls and fire doors. Ventilation and cable penetrations in fire protection walls are secured with special sealing systems and self-closing fire dampers.

The dynamic fire protection concept ensures that structural modifications can be incorporated into fire protection measures without impairing their effectiveness.

### Regular training for emergencies and fire protection

Our designated fire protection officers and trained fire protection assistants are in regular contact with the fire department and participate in training and emergency drills. In addition, regular evacuation drills are conducted.

## Network and attack protection

### Redundant and highly available network infrastructure (99.9% network availability in accordance with GTC)

Hetzner's network consists of multiple interconnected and redundant connections between the company's own data center locations and external POP locations. Within the data center, core routers connect the access routers, which in turn terminate the customer servers. The connection to the Internet is established via peering points, transit, and private peerings. A current and detailed overview of the peering points, transit, and private peerings is available on our website.

This network infrastructure creates a highly available N-to-M link between the network nodes and customer servers.

### Continuously active DDoS recognition

Our continuously active DDoS recognition system constantly analyzes traffic and detects attacks at an early stage. Malicious traffic is automatically filtered before it reaches the target systems. This reduces the impact of DDoS attacks and helps to maintain system availability as effectively as possible. Our DDoS protection is based on powerful hardware and sophisticated and complex filtering technology.

### Use of firewall and port management

Managed servers: Using our firewall, we monitor and filter traffic based on internally defined rules. In addition, we manage port rules to minimize the use of network ports as much as possible. Using konsoleH, you can request that ports be enabled or restricted.

Web hosting, Storage Shares, Storage Boxes, Object Storage: Using our firewall, we monitor and filter traffic based on internally defined rules. In addition, we manage port rules to minimize the use of network ports as much as possible.

Managed servers, web hosting, Storage Shares, Object Storage: To protect our infrastructure against common threats, we also implement a combination of several security solutions, including: • virus scanners to detect and remove malicious software, • firewalls to prevent unauthorized access, • encryption programs to protect sensitive data, • spam filters to block unwanted or potentially harmful emails.

### Individually configurable firewall

Dedicated servers: We provide a stateless firewall for our dedicated servers, which is configured on the switch port. You as the customer can define your own filter rules for incoming and outgoing traffic.

Cloud servers: We provide a stateful firewall for our Cloud servers. You as the customer can also define your own filter rules for incoming and outgoing traffic.

Object Storage: You as the customer can create access control lists (ACLs) to individually control access to a bucket on IP level and to restrict or block access if necessary.

### Hetzner-managed firewall with 24/7 monitoring

Managed servers: We take care of system security, including the configuration and maintenance of firewalls. Our administrator team monitors the systems 24/7. If required, you can request individual firewall settings via our support.

Storage Shares, Storage Boxes: We operate and maintain firewalls and relevant port management centrally and monitor the systems 24/7.

## Backup and system protection

### Backup and recovery plan

Cloud servers: If the corresponding option has been booked, the virtual disk included in the Cloud Server is automatically backed up daily. The last 7 backups are available. Once an eighth backup has been successfully created, the oldest backup is marked for deletion. In addition, you can create snapshots. Snapshots are not tied to the server and remain available even if the server is deleted.

Managed servers: We make automated daily backups of your data with our managed servers. For virtual machines, you have access to the backups from the last 7 days. For physical machines, you have access to the backups from the last 14 days. Important note: For older managed server models, a backup add-on may be required. Please contact our support team for additional information.

Web hosting: We make daily backups of the data on your web hosting account. You have access to the backups from the last 14 days.

Storage Shares: We make automated backups of the data on your Storage Shares several times per day in the form of snapshots. The database is first backed up within the file system and included in the snapshot. To ensure data security and availability, the snapshot is transferred to a separate server. You have access to the backups from the last 7 days. Important note: We explicitly recommend that you maintain your own independent backup in addition to this.

Storage Box: Our Storage Boxes include a snapshot feature that you as the customer can use independently. Depending on the size, different numbers of snapshots are available. Important note: Snapshots are not complete backups. We explicitly recommend that you maintain your own independent backup in addition to this.

Object Storage: You can store your data by creating copies of your S3 buckets in additional data centers. Important note: This does not constitute a complete backup. We explicitly recommend that you maintain your own independent backup in addition to this.

### Disk mirroring

Cloud servers, Managed servers, web hosting, Storage Shares, Storage Boxes: To protect against data loss, different disk mirroring and data replication methods are used depending on the product and intended use: Cloud servers primarily use RAID 10 configurations as well as cross-server replication in distributed storage clusters (e.g., Ceph). Managed servers and web hosting currently use RAID 1 mirroring to mitigate the failure of individual disks. Storage Shares and Storage Boxes use parity-based RAID methods (at least RAID 5, typically RAID 6 or RAID 60) to ensure increased fault tolerance and availability.

Object Storage: The Ceph storage system ensures high fault tolerance and availability through distributed data replication. Data is stored redundantly across multiple servers.

## Procedures for regular testing, assessment, and evaluation

Regularly testing, assessing, and evaluating the data protection and security standards ensures that the measures stay in compliance with regulations and improve over time.

| Measures                                                                                                                | Implementation   |
|-------------------------------------------------------------------------------------------------------------------------|------------------|
| Data protection and information security management system (DMS, ISMS)                                                  | ✓                |
| Employment of a data protection and information security officer who is integrated into the operational processes       | ✓                |
| Data-protection-friendly default settings (privacy by default and privacy by design)                                    | ✓                |
| Incident response management                                                                                            | ✓                |
| Certifications according to ISO 27001, § 8a BSI-KritisV and BSI C5 Type 2 certification                                 | ✓                |
| Annual review of TOMs by external service provider                                                                      | ✓                |
| Annual review of the proper calculation and billing of connection charges by expert opinion in accordance with § 63 TKG | ✓                |
| EMAS certification (ISO 14001) of the environmental management system at German locations                               | ✓                |

### TOMs details - Procedures for regular testing, assessment, and evaluation

Regular testing, assessment, and evaluation procedures ensure the continuous compliance with and improvement of data protection and security standards.

**Data protection and information security management system (DMS, ISMS)** Our data protection and information security management systems (DMS and ISMS) ensure that we protect all data and information in accordance with statutory and regulatory requirements. They include technical, organizational, and personnel-related measures to integrate data protection and information security sustainably into our company processes.

Hetzner has operated an information security management system (ISMS) since 2016, which is certified according to ISO/IEC 27001:2022. The effectiveness of the ISMS is regularly reviewed through internal and external audits. Further information is available [here](https://www.hetzner.com/unternehmen/zertifizierung/) .

As an operator of critical infrastructure (KRITIS), Hetzner is subject to additional legal requirements in accordance with § 8a of the German BSIG in conjunction with the BSI-KritisV. Compliance with these requirements is documented as part of the prescribed audit and verification procedures.

In addition, for cloud services, Hetzner holds a BSI C5:2020 Type 2 attestation, which confirms the implementation and effectiveness of the requirements over a defined audit period.

Further information about certifications can be found in our [Docs](https://docs.hetzner.com/general/company-and-policy/information-security-at-hetzner) .

**Employment of a data protection and information security officer who is integrated into operational processes** Hetzner Online GmbH employs a data protection officer as well as an information security officer. Both are integrated into all relevant operational processes through the data protection and information security management systems.

**Data-protection-friendly default settings (privacy by default and privacy by design)** During software development, we take data protection-friendly default settings (privacy by default) and data protection-compliant system design (privacy by design) into account.

**Incident response management** We have an incident response management system in place to detect security incidents at an early stage, assess them, and initiate appropriate countermeasures.

**Certifications according to ISO 27001, § 8a BSI-KritisV and BSI C5 Type 2 certification** The certifications listed above are regularly reviewed as part of the corresponding audit procedures. Hetzner provides information about its certifications on its website and in its documentation.

**Annual review of TOMs by external service provider** The implementation of the technical and organizational measures is reviewed annually by an external service provider.

The audit report is made available automatically to customers who have concluded a Data Processing Agreement (DPA) via the customer portal. It can be accessed via the [customer portal](https://accounts.hetzner.com/account/dpa) .

**Annual review of the proper calculation and billing of connection charges by expert opinion in accordance with § 63 TKG** The proper calculation and billing of connection charges is reviewed once per year by a publicly appointed and sworn expert.

Since this is an internal expert report, it cannot be disclosed to third parties in accordance with internal compliance regulations.

**EMAS certification (ISO 14001) of the environmental management system at German locations** Hetzner's German locations are registered under EMAS. EMAS is a voluntary EU environmental management standard that goes beyond traditional environmental management requirements and includes a validated environmental statement.

As part of the EMAS registration, we regularly review our environmental performance, implement improvement measures, and report transparently on our progress.

Further information can be found on our [website](https://www.hetzner.com/unternehmen/nachhaltigkeit/) .

###### Table of Contents