// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SupplyChain {
    
    // Product stages in supply chain
    enum Stage {
        Produced,
        Processed, 
        Shipped,
        Received,
        Sold
    }
    
    // Stakeholder types
    enum StakeholderType {
        Farmer,
        Distributor,
        Retailer,
        Consumer
    }
    
    // Product structure
    struct Product {
        uint256 id;
        string name;
        string origin;
        address farmer;
        uint256 harvestDate;
        uint256 price;
        Stage currentStage;
        bool exists;
    }
    
    // Stakeholder structure
    struct Stakeholder {
        address stakeholderAddress;
        string name;
        StakeholderType stakeholderType;
        bool isRegistered;
    }
    
    // Transaction structure for tracking
    struct Transaction {
        uint256 productId;
        address from;
        address to;
        uint256 timestamp;
        uint256 price;
        Stage stage;
    }
    
    // State variables
    mapping(uint256 => Product) public products;
    mapping(address => Stakeholder) public stakeholders;
    mapping(uint256 => Transaction[]) public productHistory;
    
    uint256 public productCounter;
    address public owner;
    
    // Events
    event ProductCreated(uint256 indexed productId, string name, address indexed farmer);
    event ProductTransferred(uint256 indexed productId, address indexed from, address indexed to, Stage stage);
    event StakeholderRegistered(address indexed stakeholder, string name, StakeholderType stakeholderType);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyRegistered() {
        require(stakeholders[msg.sender].isRegistered, "Stakeholder not registered");
        _;
    }
    
    modifier productExists(uint256 _productId) {
        require(products[_productId].exists, "Product does not exist");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        productCounter = 0;
    }
    
    // Register stakeholder
    function registerStakeholder(
        string memory _name,
        StakeholderType _type
    ) public {
        require(!stakeholders[msg.sender].isRegistered, "Stakeholder already registered");
        
        stakeholders[msg.sender] = Stakeholder({
            stakeholderAddress: msg.sender,
            name: _name,
            stakeholderType: _type,
            isRegistered: true
        });
        
        emit StakeholderRegistered(msg.sender, _name, _type);
    }
    
    // Create new product (only farmers)
    function createProduct(
        string memory _name,
        string memory _origin,
        uint256 _price
    ) public onlyRegistered returns (uint256) {
        require(
            stakeholders[msg.sender].stakeholderType == StakeholderType.Farmer,
            "Only farmers can create products"
        );
        
        productCounter++;
        
        products[productCounter] = Product({
            id: productCounter,
            name: _name,
            origin: _origin,
            farmer: msg.sender,
            harvestDate: block.timestamp,
            price: _price,
            currentStage: Stage.Produced,
            exists: true
        });
        
        // Add initial transaction
        productHistory[productCounter].push(Transaction({
            productId: productCounter,
            from: address(0),
            to: msg.sender,
            timestamp: block.timestamp,
            price: _price,
            stage: Stage.Produced
        }));
        
        emit ProductCreated(productCounter, _name, msg.sender);
        return productCounter;
    }
    
    // Transfer product to next stage
    function transferProduct(
        uint256 _productId,
        address _to,
        uint256 _price,
        Stage _newStage
    ) public onlyRegistered productExists(_productId) {
        Product storage product = products[_productId];
        
        // Basic validation
        require(_newStage > product.currentStage, "Invalid stage transition");
        require(stakeholders[_to].isRegistered, "Receiver not registered");
        
        // Update product stage and price
        product.currentStage = _newStage;
        product.price = _price;
        
        // Add transaction to history
        productHistory[_productId].push(Transaction({
            productId: _productId,
            from: msg.sender,
            to: _to,
            timestamp: block.timestamp,
            price: _price,
            stage: _newStage
        }));
        
        emit ProductTransferred(_productId, msg.sender, _to, _newStage);
    }
    
    // Get product details
    function getProduct(uint256 _productId) public view productExists(_productId) 
        returns (
            uint256 id,
            string memory name,
            string memory origin,
            address farmer,
            uint256 harvestDate,
            uint256 price,
            Stage currentStage
        ) {
        Product memory product = products[_productId];
        return (
            product.id,
            product.name,
            product.origin,
            product.farmer,
            product.harvestDate,
            product.price,
            product.currentStage
        );
    }
    
    // Get product history
    function getProductHistory(uint256 _productId) public view productExists(_productId) 
        returns (Transaction[] memory) {
        return productHistory[_productId];
    }
    
    // Get stakeholder info
    function getStakeholder(address _address) public view 
        returns (
            string memory name,
            StakeholderType stakeholderType,
            bool isRegistered
        ) {
        Stakeholder memory stakeholder = stakeholders[_address];
        return (
            stakeholder.name,
            stakeholder.stakeholderType,
            stakeholder.isRegistered
        );
    }
    
    // Get all products (for demonstration - in production, use pagination)
    function getAllProducts() public view returns (uint256[] memory) {
        uint256[] memory productIds = new uint256[](productCounter);
        for (uint256 i = 1; i <= productCounter; i++) {
            productIds[i-1] = i;
        }
        return productIds;
    }
}