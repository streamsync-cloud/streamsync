import { getContainableTypes } from "../core/typeHierarchy";
import {
	Core,
	BuilderManager,
	Component,
	ClipboardOperation,
	ComponentMap,
} from "../streamsyncTypes";

export function useComponentActions(ss: Core, ssbm: BuilderManager) {
	function generateNewComponentId() {
		const radix = 36;
		let newId = "";

		const randomArr = new Uint16Array(16);
		window.crypto.getRandomValues(randomArr);

		randomArr.forEach((n) => {
			newId += (n % radix).toString(radix);
		});

		return newId;
	}

	/**
	 * Moves a component up within its current container.
	 * Mutates the component and its previous sibling.
	 */
	function moveComponentUp(componentId: Component["id"]): void {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const position = component.position;
		if (position == 0) return;
		const parent = ss.getComponentById(component.parentId);
		if (!parent) return;

		const previousSibling = ss
			.getComponents(parent.id, { includeBMC: true, includeCMC: false })
			.filter((c) => c.position == position - 1)[0];

		// MUTATIONS

		const transactionId = `move-up-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move up`);

		ssbm.registerPreMutation(previousSibling);
		previousSibling.position++;
		ssbm.registerPostMutation(previousSibling);

		ssbm.registerPreMutation(component);
		component.position--;
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Moves a component down within its existing container.
	 * Mutates the component and its next sibling.
	 */
	function moveComponentDown(componentId: Component["id"]): void {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const parent = ss.getComponentById(component.parentId);
		if (!parent) return;
		const position = component.position;
		if (position == -2) return; // Positionless

		const positionfulSiblings = ss
			.getComponents(parent.id, { includeBMC: true, includeCMC: false })
			.filter((c) => c.position !== -2);
		if (position >= positionfulSiblings.length - 1) {
			return;
		}

		const nextSibling = positionfulSiblings.filter(
			(c) => c.position == position + 1,
		)[0];

		const transactionId = `move-down-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move down`);
		ssbm.registerPreMutation(nextSibling);
		nextSibling.position--;
		ssbm.registerPostMutation(nextSibling);
		ssbm.registerPreMutation(component);
		component.position++;
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Moves a component to a different container
	 *
	 * @param componentId Id of the target component
	 * @param newParentId Id of the new parent component
	 * @param newPosition Position of the component within the new parent
	 * @returns
	 */
	function moveComponent(
		componentId: Component["id"],
		newParentId: Component["id"],
		newPosition?: number,
	) {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const currentParentComponent = ss.getComponentById(component.parentId);
		if (!currentParentComponent) return;
		if (componentId == newParentId) return;
		if (currentParentComponent.id == newParentId && newPosition === null)
			return;
		const transactionId = `move-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Move`);
		ssbm.registerPreMutation(component);
		repositionHigherSiblings(componentId, -1);
		component.position =
			newPosition ??
			getNextInsertionPosition(newParentId, component.type);
		component.parentId = newParentId;
		repositionHigherSiblings(componentId, 1);
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	function createComponent(
		type: string,
		parentId: Component["id"],
		position?: number,
	) {
		const newId = generateNewComponentId();
		const definition = ss.getComponentDefinition(type);
		const { fields } = definition;
		const initContent = {};
		Object.entries(fields ?? {}).map(([fieldKey, field]) => {
			initContent[fieldKey] = field.init;
		});

		const component = {
			id: newId,
			type,
			parentId,
			content: initContent,
			handlers: {},
			position: position ?? getNextInsertionPosition(parentId, type),
			visible: true,
		};

		return component;
	}

	/**
	 * Creates a component of the given type and inserts it.
	 *
	 * @param type Type of the component to be created
	 * @param parentId Id of the existing component that will contain the new component
	 * @param position Position within the parent component
	 * @returns Id of the newly created component
	 */
	function createAndInsertComponent(
		type: string,
		parentId: Component["id"],
		position?: number,
	): Component["id"] {
		const component = createComponent(type, parentId, position);
		const transactionId = `create-${component.id}`;
		ssbm.openMutationTransaction(transactionId, `Create`);
		ss.addComponent(component);
		repositionHigherSiblings(component.id, 1);
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
		return component.id;
	}

	/**
	 * Moves target component's higher siblings, which are components that share the same
	 * parent and have a higher position than the target component.
	 *
	 * @param componentId Id of the target component
	 * @param delta How many position units to add to higher siblings
	 */
	function repositionHigherSiblings(
		componentId: Component["id"],
		delta: number,
	) {
		const component = ss.getComponentById(componentId);
		const positionless = ss.getComponentDefinition(
			component.type,
		).positionless;
		if (positionless) return;
		const siblings = ss
			.getComponents(component.parentId, {
				includeBMC: true,
				includeCMC: false,
			})
			.filter((c) => c.id !== componentId);
		const higherSiblings = siblings.filter(
			(siblingComponent) =>
				siblingComponent.position >= component.position,
		);
		higherSiblings.map((c) => {
			ssbm.registerPreMutation(c);
			c.position += delta;
			ssbm.registerPostMutation(c);
		});
	}

	/**
	 * Returns a subtree (component array where item 0 is the root) for a target
	 * component and its descendents.
	 *
	 * @param componentId Id of the target component
	 * @returns Subtree
	 */
	function getFlatComponentSubtree(
		componentId: Component["id"],
	): Component[] {
		const component = ss.getComponentById(componentId);
		const subtree: Component[] = [];
		const pushToSubtreeRecursively = (rootComponent: Component) => {
			const children = ss.getComponents(rootComponent.id);
			subtree.push(rootComponent);
			children.map((child) => pushToSubtreeRecursively(child));
		};
		pushToSubtreeRecursively(component);
		return subtree;
	}

	/**
	 * Removes a component and all its descendents
	 *
	 * @param componentId Id of the target component
	 */
	function removeComponentSubtree(componentId: Component["id"]): void {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const parentId = ss.getComponentById(componentId).parentId;

		const transactionId = `delete-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Delete`);
		if (parentId) {
			repositionHigherSiblings(component.id, -1);
		}
		const subtree = getFlatComponentSubtree(componentId);
		subtree.map((c) => ss.deleteComponent(c.id));
		subtree.map((c) => {
			ssbm.registerPreMutation(c);
			ss.deleteComponent(c.id);
		});
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Whether a target component is the root
	 */
	function isRoot(targetId: Component["id"]): boolean {
		return targetId == "root";
	}

	/**
	 * Whether a component can be dragged.
	 */
	function isDraggingAllowed(targetId: Component["id"]): boolean {
		const component = ss.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/**
	 * Whether a component can be added to the target component.
	 */
	function isAddAllowed(targetId: Component["id"]): boolean {
		const component = ss.getComponentById(targetId);
		return (
			!component?.isCodeManaged &&
			ss.getContainableTypes(targetId).length > 0
		);
	}

	/**
	 * Whether a component can be copied into the clipboard.
	 */
	function isCopyAllowed(targetId: Component["id"]): boolean {
		return !isRoot(targetId);
	}

	/**
	 * Whether a component can be cut and placed in the clipboard.
	 */
	function isCutAllowed(targetId: Component["id"]): boolean {
		const component = ss.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/**
	 * Whether a component can be deleted.
	 */
	function isDeleteAllowed(targetId: Component["id"]): boolean {
		const component = ss.getComponentById(targetId);
		return !isRoot(targetId) && !component?.isCodeManaged;
	}

	/**
	 * Whether it's possible to go to (select) a component's parent.
	 */
	function isGoToParentAllowed(targetId: Component["id"]): boolean {
		return !isRoot(targetId);
	}

	/**
	 * Go to (select) a target component's parent.
	 *
	 * @param targetId Id of the target component
	 * @param targetInstancePath Flattened instance path of a specific component instance
	 */
	function goToParent(
		targetId: Component["id"],
		targetInstancePath?: string,
	) {
		const targetComponent = ss.getComponentById(targetId);
		if (!targetComponent) return;
		const parentId = targetComponent.parentId;
		if (!parentId) return;

		let parentInstancePath: string;
		if (targetInstancePath) {
			parentInstancePath = targetInstancePath
				.split(",")
				.slice(0, -1)
				.join(",");
		}
		ssbm.setSelection(parentId, parentInstancePath);
	}

	/**
	 * Returns whether the components in a subtree can be incorporated
	 * to the system.
	 */
	function isSubtreeIngestable(subtree: Component[]) {
		/**
		 * This is a non-trivial operation given the complexity
		 * created by inheritance mechanisms in component parenting.
		 *
		 * For example, a Repeater with a nested Repeater with a Column
		 * can only be pasted in a Column Container. But a Repeater with a Section
		 * can be pasted almost anywhere.
		 */

		if (subtree.length == 0) return false;

		/*
		A component map is created by combining existing elements
		with the tentative elements in the subtree.
		*/

		const componentMap: ComponentMap = {};
		[...ss.getComponents(), ...subtree].forEach((component) => {
			componentMap[component.id] = component;
		});

		const isViable = subtree
			.map((component) => {
				const containableTypes = getContainableTypes(
					componentMap,
					component.parentId,
				);
				return containableTypes.includes(component.type);
			})
			.every((item) => item);
		return isViable;
	}

	/**
	 * Returns whether the current contents of the internal clipboard can be
	 * pasted to the target component.
	 */
	function isPasteAllowed(targetId: Component["id"]): boolean {
		const component = ss.getComponentById(targetId);
		if (!component || component.isCodeManaged) return false;
		const clipboard = ssbm.getClipboard();
		if (clipboard === null) return false;
		const { jsonSubtree } = clipboard;
		const subtree: Component[] = JSON.parse(jsonSubtree);
		if (subtree.length == 0) return false;

		// Mutate the subtree to reflect tentative parent

		subtree[0].parentId = targetId;
		return isSubtreeIngestable(subtree);
	}

	/**
	 * Returns whether the component can be moved up, and whether it can
	 * be moved down.
	 *
	 * @param targetId Id of the target Component
	 */
	function getEnabledMoves(targetId: Component["id"]) {
		const getPositionableChildrenCount = (parentId: Component["id"]) => {
			const children = ss.getComponents(parentId, {
				includeBMC: true,
				includeCMC: false,
			});
			const positionableChildren = children.filter((c) => {
				const positionless = ss.getComponentDefinition(
					c.type,
				)?.positionless;
				if (positionless) return false;
				return true;
			});
			return positionableChildren.length;
		};

		const component = ss.getComponentById(targetId);
		if (!component || component.isCodeManaged) {
			return { up: false, down: false };
		}
		const definition = ss.getComponentDefinition(component.type);
		if (definition.positionless) return { up: false, down: false };
		const positionableSiblingCount = component.parentId
			? getPositionableChildrenCount(component.parentId)
			: 0;
		const isUpEnabled =
			positionableSiblingCount > 0 && component.position > 0;
		const isDownEnabled =
			positionableSiblingCount > 0 &&
			component.position < positionableSiblingCount - 1;
		return { up: isUpEnabled, down: isDownEnabled };
	}

	/**
	 * Cuts a component and its descendents and places them in the internal clipboard.
	 * @param componentId Id of the component to be cut
	 */
	function cutComponent(componentId: Component["id"]): void {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		ssbm.setClipboard({
			operation: ClipboardOperation.Cut,
			jsonSubtree: JSON.stringify(getFlatComponentSubtree(componentId)),
		});
		ssbm.setSelection(null);
		removeComponentSubtree(componentId);
		ss.sendComponentUpdate();
	}

	/**
	 * Returns a deep copy of the given subtree with all its component IDs
	 * regenerated.
	 */
	function getNewSubtreeWithRegeneratedIds(subtree: Component[]) {
		const deepCopiedSubtree: Component[] = JSON.parse(
			JSON.stringify(subtree),
		);
		deepCopiedSubtree.forEach((c) => {
			delete c.isCodeManaged;
			const newId = generateNewComponentId();
			deepCopiedSubtree
				.filter((nc) => nc.id !== c.id)
				.map((nc) => {
					if (nc.parentId == c.id) {
						nc.parentId = newId;
					}
				});
			c.id = newId;
		});
		return deepCopiedSubtree;
	}

	/**
	 * Copies a component and its descendents into the clipboard
	 * @param componentId Id of the component to be copied
	 * @returns
	 */
	function copyComponent(componentId: Component["id"]): void {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const subtree = getFlatComponentSubtree(componentId);
		const newSubtree = getNewSubtreeWithRegeneratedIds(subtree);

		ssbm.setClipboard({
			operation: ClipboardOperation.Copy,
			jsonSubtree: JSON.stringify(newSubtree),
		});
	}

	/**
	 * Pastes the contents of the clipboard into a given component
	 * @param targetParentId Id of the component where to paste the clipboard
	 */
	function pasteComponent(targetParentId: Component["id"]): void {
		const targetParent = ss.getComponentById(targetParentId);
		if (!targetParent) return;

		const clipboard = ssbm.getClipboard();
		if (clipboard === null) return;
		const { operation, jsonSubtree } = clipboard;
		const subtree = JSON.parse(jsonSubtree);
		if (operation == ClipboardOperation.Cut)
			return pasteCutComponent(targetParentId, subtree);
		if (operation == ClipboardOperation.Copy)
			return pasteCopyComponent(targetParentId, subtree);
	}

	/**
	 * Pastes a subtree that has been obtained by a cut operation.
	 */
	function pasteCutComponent(
		targetParentId: Component["id"],
		subtree: Component[],
	) {
		// MUTATION

		ssbm.setClipboard(null);
		const rootComponent = subtree[0];
		rootComponent.parentId = targetParentId;
		rootComponent.position = getNextInsertionPosition(
			targetParentId,
			rootComponent.type,
		);

		const transactionId = `paste-cut-${targetParentId}`;
		ssbm.openMutationTransaction(transactionId, `Paste from cut`);
		subtree.map((c) => {
			ss.addComponent(c);
			ssbm.registerPostMutation(c);
		});
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Pastes a subtree that has been obtained via a copy operation.
	 */
	function pasteCopyComponent(
		targetParentId: Component["id"],
		subtree: Component[],
	) {
		// Regenerate clipboard for future pastes

		ssbm.setClipboard({
			operation: ClipboardOperation.Copy,
			jsonSubtree: JSON.stringify(
				getNewSubtreeWithRegeneratedIds(subtree),
			),
		});

		// MUTATION

		const rootComponent = subtree[0];
		rootComponent.parentId = targetParentId;
		rootComponent.position = getNextInsertionPosition(
			targetParentId,
			rootComponent.type,
		);

		const transactionId = `paste-copy-${targetParentId}`;
		ssbm.openMutationTransaction(transactionId, `Paste from copy`);
		subtree.map((c) => {
			ss.addComponent(c);
			ssbm.registerPostMutation(c);
		});
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Returns the default position for the next insertion into the given component.
	 */
	function getNextInsertionPosition(
		targetParentId: Component["id"],
		childType: Component["type"],
	) {
		const positionless = ss.getComponentDefinition(childType).positionless;
		if (positionless) {
			return -2;
		}

		const positionfulChildren = ss
			.getComponents(targetParentId, {
				includeBMC: true,
				includeCMC: false,
			})
			.filter((c) => c.position !== -2);

		if (positionfulChildren.length > 0) {
			const position = Math.max(
				Math.max(
					...positionfulChildren.map((c: Component) => c.position),
				) + 1,
				0,
			);
			return position;
		} else {
			return 0;
		}
	}

	/**
	 * Get a snapshot of the current state of mutations transactions:
	 * - Whether Undo and Redo transactions are available
	 * - A short description of Undo and Redo transactions
	 */
	function getUndoRedoSnapshot() {
		const snapshot = ssbm.getMutationTransactionsSnapshot();
		return {
			isUndoAvailable: !!snapshot.undo,
			isRedoAvailable: !!snapshot.redo,
			undoDesc: snapshot.undo?.desc,
			redoDesc: snapshot.redo?.desc,
		};
	}

	/**
	 * Undo mutation transaction.
	 */
	function undo() {
		const transaction = ssbm.consumeUndoTransaction();
		if (!transaction) return;

		Object.entries(transaction.mutations).forEach(
			([mutationId, mutation]) => {
				if (mutation.jsonPre && mutation.jsonPost) {
					ss.addComponent(JSON.parse(mutation.jsonPre));
					return;
				}

				if (!mutation.jsonPre && mutation.jsonPost) {
					ss.deleteComponent(mutationId);
					return;
				}

				if (mutation.jsonPre && !mutation.jsonPost) {
					ss.addComponent(JSON.parse(mutation.jsonPre));
					return;
				}
			},
		);
		ss.sendComponentUpdate();
	}

	/**
	 * Redo previously undone mutation transaction.
	 */
	function redo() {
		const transaction = ssbm.consumeRedoTransaction();
		if (!transaction) return;

		Object.entries(transaction.mutations).forEach(
			([mutationId, mutation]) => {
				if (mutation.jsonPre && mutation.jsonPost) {
					ss.addComponent(JSON.parse(mutation.jsonPost));
					return;
				}

				if (!mutation.jsonPre && mutation.jsonPost) {
					ss.addComponent(JSON.parse(mutation.jsonPost));
					return;
				}

				if (mutation.jsonPre && !mutation.jsonPost) {
					ss.deleteComponent(mutationId);
					return;
				}
			},
		);
		ss.sendComponentUpdate();
	}

	/**
	 * Set a value for a component content field
	 */
	function setContentValue(
		componentId: Component["id"],
		fieldKey: string,
		value: string,
	) {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const transactionId = `edit-${componentId}-content-${fieldKey}`;
		ssbm.openMutationTransaction(transactionId, `Edit property`, true);
		ssbm.registerPreMutation(component);

		component.content[fieldKey] = value;

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Set the value for a component's visibility.
	 */
	function setVisibleValue(
		componentId: Component["id"],
		visible: Component["visible"],
	) {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const transactionId = `change-visibility-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Change visibility`, true);
		ssbm.registerPreMutation(component);

		if (visible === true && typeof component.visible != "undefined") {
			delete component.visible;
		} else {
			component.visible = visible;
		}

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Set a component's two-way binding.
	 */
	function setBinding(
		componentId: Component["id"],
		stateRef: Component["binding"]["stateRef"],
		targetEventType?: Component["binding"]["eventType"],
	) {
		const component = ss.getComponentById(componentId);
		if (!component) return;

		let eventType: string;
		if (targetEventType) {
			eventType = targetEventType;
		} else {
			const definition = ss.getComponentDefinition(component.type);
			const events = Object.entries(definition.events).filter(
				([eventType, event]) => event.bindable,
			);
			const bindableEventTypes = events.map(
				([eventType, event]) => eventType,
			);
			eventType = bindableEventTypes?.[0];
		}

		if (!eventType) return;

		const transactionId = `change-binding-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Change binding`, true);
		ssbm.registerPreMutation(component);

		if (stateRef) {
			component.binding = {
				eventType,
				stateRef,
			};
		} else {
			delete component.binding;
		}
		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	/**
	 * Set an event handler for a component.
	 */
	function setHandlerValue(
		componentId: Component["id"],
		eventType: string,
		userFunction: string,
	) {
		const component = ss.getComponentById(componentId);
		if (!component) return;
		const transactionId = `set-handler-${componentId}`;
		ssbm.openMutationTransaction(transactionId, `Set event handler`, true);
		ssbm.registerPreMutation(component);

		if (userFunction) {
			if (!component.handlers) {
				component.handlers = {};
			}
			component.handlers[eventType] = userFunction;
		} else {
			delete component.handlers[eventType];
			if (Object.keys(component.handlers).length == 0) {
				delete component.handlers;
			}
		}

		ssbm.registerPostMutation(component);
		ssbm.closeMutationTransaction(transactionId);
		ss.sendComponentUpdate();
	}

	function getContainingPageId(
		componentId: Component["id"],
	): Component["id"] {
		const component = ss.getComponentById(componentId);
		if (!component || component.type == "root") return null;
		if (component.type == "page") return componentId;
		return getContainingPageId(component.parentId);
	}

	async function goToComponentParentPage(componentId: Component["id"]) {
		const component = ss.getComponentById(componentId);
		const componentDefinition = ss.getComponentDefinition(
			component.type,
		)?.name;
		if (!componentDefinition) return; // Unknown component, not rendered
		ss.setActivePageId(getContainingPageId(componentId));
	}

	return {
		moveComponent,
		moveComponentUp,
		moveComponentDown,
		cutComponent,
		copyComponent,
		pasteComponent,
		createAndInsertComponent,
		removeComponentSubtree,
		isPasteAllowed,
		undo,
		redo,
		setContentValue,
		setVisibleValue,
		setBinding,
		getUndoRedoSnapshot,
		setHandlerValue,
		isAddAllowed,
		isCopyAllowed,
		isCutAllowed,
		isDeleteAllowed,
		isGoToParentAllowed,
		isDraggingAllowed,
		getEnabledMoves,
		goToParent,
		goToComponentParentPage,
	};
}
